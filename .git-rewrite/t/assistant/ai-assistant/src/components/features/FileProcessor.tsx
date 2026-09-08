import React, { useState, useCallback } from 'react';
import { useApp } from '../../contexts/AppContext';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { ScrollArea } from '../ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import {
  Upload,
  File,
  FileText,
  Image as ImageIcon,
  Download,
  Trash2,
  Eye,
  Brain,
  Loader2,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import { cn } from '../../lib/utils';
import { format } from 'date-fns';

interface ProcessedFile {
  id: string;
  file: File;
  name: string;
  type: string;
  size: string;
  uploadedAt: Date;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  progress: number;
  preview?: string;
  analysis?: {
    summary: string;
    keyPoints: string[];
    wordCount?: number;
    pageCount?: number;
    fileType: string;
  };
  error?: string;
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const getFileIcon = (type: string) => {
  if (type.startsWith('image/')) return <ImageIcon className="h-5 w-5" />;
  if (type === 'application/pdf' || type.includes('document')) return <FileText className="h-5 w-5" />;
  return <File className="h-5 w-5" />;
};

export default function FileProcessor() {
  const { addMessage } = useApp();
  const [files, setFiles] = useState<ProcessedFile[]>([]);
  const [dragOver, setDragOver] = useState(false);

  const simulateFileProcessing = async (processedFile: ProcessedFile) => {
    // Simulate upload progress
    for (let progress = 0; progress <= 100; progress += 10) {
      await new Promise(resolve => setTimeout(resolve, 100));
      setFiles(prev => prev.map(f => 
        f.id === processedFile.id ? { ...f, progress } : f
      ));
    }

    // Change to processing status
    setFiles(prev => prev.map(f => 
      f.id === processedFile.id ? { ...f, status: 'processing', progress: 0 } : f
    ));

    // Simulate processing
    for (let progress = 0; progress <= 100; progress += 5) {
      await new Promise(resolve => setTimeout(resolve, 50));
      setFiles(prev => prev.map(f => 
        f.id === processedFile.id ? { ...f, progress } : f
      ));
    }

    // Generate analysis based on file type
    let analysis: ProcessedFile['analysis'];
    
    if (processedFile.type.startsWith('image/')) {
      analysis = {
        summary: "This image appears to show a business or technical diagram. The visual elements suggest it contains important information that could be useful for analysis or reference.",
        keyPoints: [
          "Clear visual presentation of information",
          "Contains structured data or workflow",
          "Professional formatting and layout",
          "Suitable for documentation purposes"
        ],
        fileType: "Image"
      };
    } else if (processedFile.type === 'application/pdf' || processedFile.type.includes('document')) {
      analysis = {
        summary: "This document contains structured information with multiple sections. The content appears to be well-organized and covers several key topics that could be valuable for research or reference.",
        keyPoints: [
          "Well-structured document with clear sections",
          "Contains valuable information and insights",
          "Professional formatting and presentation",
          "Suitable for analysis and summarization"
        ],
        wordCount: Math.floor(Math.random() * 5000) + 500,
        pageCount: Math.floor(Math.random() * 20) + 1,
        fileType: "Document"
      };
    } else {
      analysis = {
        summary: "This file has been successfully processed and is ready for analysis. The content structure suggests it contains valuable information.",
        keyPoints: [
          "File successfully processed",
          "Content ready for analysis",
          "Structured information detected",
          "Available for AI interaction"
        ],
        fileType: "Text File"
      };
    }

    // Complete processing
    setFiles(prev => prev.map(f => 
      f.id === processedFile.id ? { 
        ...f, 
        status: 'completed', 
        progress: 100, 
        analysis 
      } : f
    ));
  };

  const handleFileUpload = useCallback((uploadedFiles: File[]) => {
    const newFiles: ProcessedFile[] = uploadedFiles.map(file => ({
      id: Date.now() + Math.random().toString(),
      file,
      name: file.name,
      type: file.type,
      size: formatFileSize(file.size),
      uploadedAt: new Date(),
      status: 'uploading',
      progress: 0,
      preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : undefined
    }));

    setFiles(prev => [...newFiles, ...prev]);

    // Process each file
    newFiles.forEach(processedFile => {
      simulateFileProcessing(processedFile);
    });
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    handleFileUpload(droppedFiles);
  }, [handleFileUpload]);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      handleFileUpload(Array.from(e.target.files));
    }
  };

  const deleteFile = (fileId: string) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const askAboutFile = (file: ProcessedFile) => {
    const prompt = `I've uploaded a file called "${file.name}". Can you help me analyze and understand its contents? Here's what I found:\n\n${file.analysis?.summary}\n\nKey points:\n${file.analysis?.keyPoints.map(point => `• ${point}`).join('\n')}`;
    addMessage(prompt, 'user');
  };

  const completedFiles = files.filter(f => f.status === 'completed');
  const processingFiles = files.filter(f => f.status === 'uploading' || f.status === 'processing');
  const errorFiles = files.filter(f => f.status === 'error');

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-6 border-b">
        <div className="flex items-center gap-2 mb-4">
          <Upload className="h-6 w-6 text-primary" />
          <h1 className="text-2xl font-bold">File Processor</h1>
        </div>
        <p className="text-muted-foreground">
          Upload and analyze documents, images, and other files with AI-powered insights
        </p>
      </div>

      {/* Upload Area */}
      <div className="p-6 border-b">
        <div
          className={cn(
            "border-2 border-dashed rounded-lg p-8 text-center transition-colors",
            dragOver ? "border-primary bg-primary/5" : "border-muted-foreground/25",
            "hover:border-primary/50 hover:bg-primary/5"
          )}
          onDrop={handleDrop}
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
        >
          <Upload className="h-10 w-10 mx-auto mb-4 text-muted-foreground" />
          <h3 className="text-lg font-semibold mb-2">Drop files here or click to upload</h3>
          <p className="text-muted-foreground mb-4">
            Support for PDF, DOC, TXT, images, and more
          </p>
          <div>
            <input
              type="file"
              multiple
              onChange={handleFileInput}
              accept=".pdf,.doc,.docx,.txt,.md,.jpg,.jpeg,.png,.gif,.webp"
              className="hidden"
              id="file-upload"
            />
            <Button asChild>
              <label htmlFor="file-upload" className="cursor-pointer">
                <Upload className="h-4 w-4 mr-2" />
                Choose Files
              </label>
            </Button>
          </div>
        </div>
      </div>

      {/* Files List */}
      <div className="flex-1 overflow-hidden">
        <Tabs defaultValue="all" className="h-full flex flex-col">
          <div className="px-6 pt-4">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="all">All ({files.length})</TabsTrigger>
              <TabsTrigger value="completed">Completed ({completedFiles.length})</TabsTrigger>
              <TabsTrigger value="processing">Processing ({processingFiles.length})</TabsTrigger>
              <TabsTrigger value="errors">Errors ({errorFiles.length})</TabsTrigger>
            </TabsList>
          </div>

          <TabsContent value="all" className="flex-1 px-6 pb-6">
            <ScrollArea className="h-full">
              <div className="space-y-4">
                {files.map(file => (
                  <FileCard key={file.id} file={file} onDelete={deleteFile} onAskAbout={askAboutFile} />
                ))}
                {files.length === 0 && (
                  <div className="text-center py-12 text-muted-foreground">
                    <File className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No files uploaded yet</p>
                  </div>
                )}
              </div>
            </ScrollArea>
          </TabsContent>

          <TabsContent value="completed" className="flex-1 px-6 pb-6">
            <ScrollArea className="h-full">
              <div className="space-y-4">
                {completedFiles.map(file => (
                  <FileCard key={file.id} file={file} onDelete={deleteFile} onAskAbout={askAboutFile} />
                ))}
                {completedFiles.length === 0 && (
                  <div className="text-center py-12 text-muted-foreground">
                    <CheckCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No completed files yet</p>
                  </div>
                )}
              </div>
            </ScrollArea>
          </TabsContent>

          <TabsContent value="processing" className="flex-1 px-6 pb-6">
            <ScrollArea className="h-full">
              <div className="space-y-4">
                {processingFiles.map(file => (
                  <FileCard key={file.id} file={file} onDelete={deleteFile} onAskAbout={askAboutFile} />
                ))}
                {processingFiles.length === 0 && (
                  <div className="text-center py-12 text-muted-foreground">
                    <Loader2 className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No files being processed</p>
                  </div>
                )}
              </div>
            </ScrollArea>
          </TabsContent>

          <TabsContent value="errors" className="flex-1 px-6 pb-6">
            <ScrollArea className="h-full">
              <div className="space-y-4">
                {errorFiles.map(file => (
                  <FileCard key={file.id} file={file} onDelete={deleteFile} onAskAbout={askAboutFile} />
                ))}
                {errorFiles.length === 0 && (
                  <div className="text-center py-12 text-muted-foreground">
                    <AlertCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No errors</p>
                  </div>
                )}
              </div>
            </ScrollArea>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

interface FileCardProps {
  file: ProcessedFile;
  onDelete: (fileId: string) => void;
  onAskAbout: (file: ProcessedFile) => void;
}

function FileCard({ file, onDelete, onAskAbout }: FileCardProps) {
  const getStatusIcon = () => {
    switch (file.status) {
      case 'uploading':
        return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />;
      case 'processing':
        return <Brain className="h-4 w-4 text-yellow-500" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
    }
  };

  const getStatusText = () => {
    switch (file.status) {
      case 'uploading': return 'Uploading...';
      case 'processing': return 'Processing...';
      case 'completed': return 'Completed';
      case 'error': return 'Error';
    }
  };

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {getFileIcon(file.type)}
            <div className="flex-1 min-w-0">
              <CardTitle className="text-base truncate">{file.name}</CardTitle>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <span>{file.size}</span>
                <span>•</span>
                <span>{format(file.uploadedAt, 'MMM d, HH:mm')}</span>
                <span>•</span>
                <div className="flex items-center gap-1">
                  {getStatusIcon()}
                  <span>{getStatusText()}</span>
                </div>
              </div>
            </div>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => onDelete(file.id)}
            className="h-8 w-8"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        {/* Progress Bar */}
        {(file.status === 'uploading' || file.status === 'processing') && (
          <div className="mb-4">
            <Progress value={file.progress} className="h-2" />
            <p className="text-xs text-muted-foreground mt-1">
              {file.status === 'uploading' ? 'Uploading' : 'Processing'} {file.progress}%
            </p>
          </div>
        )}

        {/* Error Message */}
        {file.status === 'error' && file.error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-600">{file.error}</p>
          </div>
        )}

        {/* Analysis Results */}
        {file.status === 'completed' && file.analysis && (
          <div className="space-y-4">
            <div>
              <h4 className="font-medium mb-2">Analysis Summary</h4>
              <p className="text-sm text-muted-foreground">{file.analysis.summary}</p>
            </div>

            <div>
              <h4 className="font-medium mb-2">Key Points</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                {file.analysis.keyPoints.map((point, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="text-primary mt-1.5">•</span>
                    <span>{point}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* File Stats */}
            <div className="flex gap-4">
              {file.analysis.wordCount && (
                <Badge variant="outline">
                  {file.analysis.wordCount.toLocaleString()} words
                </Badge>
              )}
              {file.analysis.pageCount && (
                <Badge variant="outline">
                  {file.analysis.pageCount} pages
                </Badge>
              )}
              <Badge variant="outline">
                {file.analysis.fileType}
              </Badge>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2">
              <Button size="sm" onClick={() => onAskAbout(file)}>
                <Brain className="h-4 w-4 mr-2" />
                Ask AI About This File
              </Button>
              {file.preview && (
                <Button variant="outline" size="sm" asChild>
                  <a href={file.preview} target="_blank" rel="noopener noreferrer">
                    <Eye className="h-4 w-4 mr-2" />
                    Preview
                  </a>
                </Button>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
