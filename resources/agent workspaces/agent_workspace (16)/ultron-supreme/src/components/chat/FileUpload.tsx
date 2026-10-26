import React, { useState, useRef } from 'react'
import { Upload, X, File, Image, FileText, Music, Video, CheckCircle } from 'lucide-react'
import { callEdgeFunction } from '@/lib/supabase'
import { useAuth } from '@/contexts/AuthContext'

interface FileUploadProps {
  sessionId: string
  onUpload: (fileData: any) => void
  onClose: () => void
}

export const FileUpload: React.FC<FileUploadProps> = ({ 
  sessionId, 
  onUpload, 
  onClose 
}) => {
  const { user } = useAuth()
  const [dragActive, setDragActive] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const getFileIcon = (type: string) => {
    if (type.startsWith('image/')) return <Image className="w-5 h-5" />
    if (type.startsWith('video/')) return <Video className="w-5 h-5" />
    if (type.startsWith('audio/')) return <Music className="w-5 h-5" />
    if (type.includes('text') || type.includes('json')) return <FileText className="w-5 h-5" />
    return <File className="w-5 h-5" />
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const handleFiles = async (files: FileList) => {
    if (files.length === 0) return

    const file = files[0]
    const maxSize = 50 * 1024 * 1024 // 50MB limit

    if (file.size > maxSize) {
      setError('File size must be less than 50MB')
      return
    }

    setUploading(true)
    setError(null)
    setSuccess(null)

    try {
      // Convert file to base64
      const reader = new FileReader()
      
      reader.onload = async () => {
        try {
          const base64Data = reader.result as string
          
          // Upload to server
          const result = await callEdgeFunction(
            'file-upload',
            {
              fileData: base64Data,
              fileName: file.name,
              fileType: file.type,
              sessionId
            },
            user?.access_token
          )

          setSuccess(`File uploaded successfully: ${file.name}`)
          onUpload(result.data)
          
          // Auto-close after success
          setTimeout(() => {
            onClose()
          }, 2000)

        } catch (uploadError) {
          setError(`Upload failed: ${uploadError instanceof Error ? uploadError.message : 'Unknown error'}`)
        } finally {
          setUploading(false)
        }
      }

      reader.onerror = () => {
        setError('Failed to read file')
        setUploading(false)
      }

      reader.readAsDataURL(file)

    } catch (err) {
      setError(`Error: ${err instanceof Error ? err.message : 'Unknown error'}`)
      setUploading(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files)
    }
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      handleFiles(e.target.files)
    }
  }

  return (
    <div className="glass-intense rounded-lg p-4 border border-red-500/30">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-orbitron font-bold text-glow-red">
          FILE UPLOAD
        </h3>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-red-400 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Upload Area */}
      <div
        className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
          dragActive 
            ? 'border-red-400 bg-red-500/10' 
            : 'border-gray-600 hover:border-red-500/50'
        }`}
        onDrop={handleDrop}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
      >
        {uploading ? (
          <div className="py-4">
            <div className="spinner-ultron mx-auto mb-4" />
            <div className="font-orbitron font-bold text-glow-red">
              UPLOADING...
            </div>
            <div className="text-sm text-gray-400 mt-2">
              Processing your file
            </div>
          </div>
        ) : success ? (
          <div className="py-4">
            <CheckCircle className="w-12 h-12 text-green-400 mx-auto mb-4 glow-subtle" />
            <div className="font-orbitron font-bold text-green-400 text-glow-blue">
              UPLOAD COMPLETE
            </div>
            <div className="text-sm text-gray-400 mt-2">
              {success}
            </div>
          </div>
        ) : (
          <div>
            <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <div className="font-orbitron font-bold text-gray-300 mb-2">
              DROP FILES HERE
            </div>
            <div className="text-sm text-gray-400 mb-4">
              or click to browse
            </div>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="btn-ultron"
              disabled={uploading}
            >
              Select Files
            </button>
          </div>
        )}

        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          onChange={handleFileInput}
          accept="image/*,video/*,audio/*,text/*,application/pdf,application/json"
        />
      </div>

      {/* Error/Success Messages */}
      {error && (
        <div className="mt-4 p-3 bg-red-900/30 border border-red-500/50 rounded-lg text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* File Type Info */}
      <div className="mt-4 text-xs text-gray-500 font-roboto">
        <div className="font-semibold mb-2">Supported formats:</div>
        <div className="grid grid-cols-2 gap-1">
          <div>• Images (JPG, PNG, GIF, WebP)</div>
          <div>• Videos (MP4, WebM, AVI)</div>
          <div>• Audio (MP3, WAV, OGG)</div>
          <div>• Documents (PDF, TXT, JSON)</div>
        </div>
        <div className="mt-2">Maximum file size: 50MB</div>
      </div>
    </div>
  )
}