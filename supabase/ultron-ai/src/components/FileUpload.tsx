import React, { useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useDropzone } from 'react-dropzone'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { supabase } from '../lib/supabase'
import { formatFileSize, formatTime } from '../lib/utils'
import {
  DocumentArrowUpIcon,
  PhotoIcon,
  EyeIcon,
  SparklesIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

interface FileItem {
  id: string
  file: File
  status: 'uploading' | 'processing' | 'completed' | 'error'
  progress: number
  url?: string
  ocrText?: string
  aiAnalysis?: string
  error?: string
}

export function FileUpload() {
  const [files, setFiles] = useState<FileItem[]>([])
  const [enableAIAnalysis, setEnableAIAnalysis] = useState(true)

  const processFile = async (file: File) => {
    const fileId = Date.now().toString()
    const fileItem: FileItem = {
      id: fileId,
      file,
      status: 'uploading',
      progress: 0
    }

    setFiles(prev => [...prev, fileItem])

    try {
      // Convert file to base64
      const base64Data = await new Promise<string>((resolve, reject) => {
        const reader = new FileReader()
        reader.onloadend = () => resolve(reader.result as string)
        reader.onerror = reject
        reader.readAsDataURL(file)
      })

      // Update status to processing
      setFiles(prev => prev.map(f => 
        f.id === fileId 
          ? { ...f, status: 'processing', progress: 50 }
          : f
      ))

      // Upload and process file
      const { data, error } = await supabase.functions.invoke('file-upload', {
        body: {
          fileData: base64Data,
          fileName: file.name,
          fileType: file.type,
          aiAnalysis: enableAIAnalysis
        }
      })

      if (error) throw error

      // Update with results
      setFiles(prev => prev.map(f => 
        f.id === fileId 
          ? {
              ...f,
              status: 'completed',
              progress: 100,
              url: data.data.fileUrl,
              ocrText: data.data.ocrText,
              aiAnalysis: data.data.aiAnalysis
            }
          : f
      ))

      toast.success('File processed successfully!')
    } catch (error: any) {
      console.error('File upload error:', error)
      setFiles(prev => prev.map(f => 
        f.id === fileId 
          ? {
              ...f,
              status: 'error',
              progress: 0,
              error: error.message
            }
          : f
      ))
      toast.error('File processing failed: ' + error.message)
    }
  }

  const onDrop = useCallback((acceptedFiles: File[]) => {
    acceptedFiles.forEach(processFile)
  }, [enableAIAnalysis])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp'],
      'video/*': ['.mp4', '.avi', '.mov', '.wmv'],
      'audio/*': ['.mp3', '.wav', '.flac'],
      'application/pdf': ['.pdf'],
      'text/*': ['.txt', '.md', '.csv']
    },
    maxSize: 50 * 1024 * 1024 // 50MB
  })

  const removeFile = (fileId: string) => {
    setFiles(prev => prev.filter(f => f.id !== fileId))
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'uploading':
      case 'processing':
        return <ClockIcon className="w-5 h-5 text-ultron-blue animate-spin" />
      case 'completed':
        return <CheckCircleIcon className="w-5 h-5 text-green-400" />
      case 'error':
        return <XCircleIcon className="w-5 h-5 text-red-400" />
      default:
        return null
    }
  }

  return (
    <div className="space-y-6">
      {/* Upload Area */}
      <Card className="glass-morphism border-ultron-blue/30">
        <CardHeader>
          <CardTitle className="text-xl font-orbitron text-white flex items-center space-x-2">
            <DocumentArrowUpIcon className="w-6 h-6 text-ultron-blue" />
            <span>File Upload & Analysis</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-all duration-300 cursor-pointer ${
              isDragActive
                ? 'border-ultron-blue bg-ultron-blue/10'
                : 'border-ultron-gray hover:border-ultron-blue/50'
            }`}
          >
            <input {...getInputProps()} />
            <motion.div
              animate={isDragActive ? { scale: 1.1 } : { scale: 1 }}
              className="space-y-4"
            >
              <DocumentArrowUpIcon className="w-16 h-16 text-ultron-blue mx-auto" />
              <div>
                <p className="text-lg font-medium text-white mb-2">
                  {isDragActive ? 'Drop files here' : 'Drag & drop files here'}
                </p>
                <p className="text-gray-400 text-sm">
                  or click to select files
                </p>
                <p className="text-gray-500 text-xs mt-2">
                  Supports images, videos, audio, PDFs, and text files (max 50MB)
                </p>
              </div>
            </motion.div>
          </div>

          <div className="mt-4 flex items-center space-x-2">
            <input
              type="checkbox"
              id="aiAnalysis"
              checked={enableAIAnalysis}
              onChange={(e) => setEnableAIAnalysis(e.target.checked)}
              className="rounded border-ultron-blue"
            />
            <label htmlFor="aiAnalysis" className="text-sm text-gray-300 flex items-center space-x-1">
              <SparklesIcon className="w-4 h-4 text-ultron-purple" />
              <span>Enable AI Analysis & OCR</span>
            </label>
          </div>
        </CardContent>
      </Card>

      {/* File List */}
      {files.length > 0 && (
        <Card className="glass-morphism border-ultron-red/30">
          <CardHeader>
            <CardTitle className="text-lg font-orbitron text-white">
              Processing Queue ({files.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <AnimatePresence>
                {files.map((fileItem) => (
                  <motion.div
                    key={fileItem.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className="bg-ultron-dark/50 rounded-lg p-4 border border-ultron-gray/30"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-3">
                        {getStatusIcon(fileItem.status)}
                        <div>
                          <p className="text-white font-medium text-sm">
                            {fileItem.file.name}
                          </p>
                          <p className="text-gray-400 text-xs">
                            {formatFileSize(fileItem.file.size)} • {fileItem.file.type}
                          </p>
                        </div>
                      </div>
                      
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeFile(fileItem.id)}
                        className="text-gray-400 hover:text-red-400"
                      >
                        <XCircleIcon className="w-4 h-4" />
                      </Button>
                    </div>

                    {/* Progress Bar */}
                    {(fileItem.status === 'uploading' || fileItem.status === 'processing') && (
                      <div className="mb-3">
                        <div className="flex justify-between text-xs mb-1">
                          <span className="text-gray-400 capitalize">
                            {fileItem.status}...
                          </span>
                          <span className="text-white">{fileItem.progress}%</span>
                        </div>
                        <div className="w-full bg-ultron-darker rounded-full h-1.5">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${fileItem.progress}%` }}
                            className="h-1.5 bg-gradient-to-r from-ultron-red to-ultron-blue rounded-full"
                          />
                        </div>
                      </div>
                    )}

                    {/* Results */}
                    {fileItem.status === 'completed' && (
                      <div className="space-y-3">
                        {fileItem.url && (
                          <div>
                            <p className="text-ultron-blue text-sm font-medium mb-1">
                              File URL:
                            </p>
                            <a
                              href={fileItem.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-xs text-gray-300 hover:text-ultron-blue break-all"
                            >
                              {fileItem.url}
                            </a>
                          </div>
                        )}
                        
                        {fileItem.ocrText && (
                          <div>
                            <p className="text-ultron-purple text-sm font-medium mb-1 flex items-center space-x-1">
                              <EyeIcon className="w-4 h-4" />
                              <span>Extracted Text (OCR):</span>
                            </p>
                            <div className="bg-ultron-darker/50 rounded p-2 text-xs text-gray-300 max-h-24 overflow-y-auto scrollbar-thin">
                              {fileItem.ocrText}
                            </div>
                          </div>
                        )}
                        
                        {fileItem.aiAnalysis && (
                          <div>
                            <p className="text-ultron-red text-sm font-medium mb-1 flex items-center space-x-1">
                              <SparklesIcon className="w-4 h-4" />
                              <span>AI Analysis:</span>
                            </p>
                            <div className="bg-ultron-darker/50 rounded p-2 text-xs text-gray-300 max-h-32 overflow-y-auto scrollbar-thin">
                              {fileItem.aiAnalysis}
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Error */}
                    {fileItem.status === 'error' && fileItem.error && (
                      <div className="bg-red-900/20 border border-red-500/30 rounded p-2">
                        <p className="text-red-400 text-sm">
                          Error: {fileItem.error}
                        </p>
                      </div>
                    )}
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}