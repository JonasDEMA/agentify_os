import { useState, useRef } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Upload, FileSpreadsheet, X } from 'lucide-react'

interface FileUploadProps {
  onFileUpload: (file: File) => void
  isUploading?: boolean
}

export function FileUpload({ onFileUpload, isUploading = false }: FileUploadProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = (file: File) => {
    if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls') || file.name.endsWith('.csv')) {
      setSelectedFile(file)
    } else {
      alert('Please select an Excel file (.xlsx, .xls, or .csv)')
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    
    const file = e.dataTransfer.files[0]
    if (file) {
      handleFileSelect(file)
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleUpload = () => {
    if (selectedFile) {
      onFileUpload(selectedFile)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Upload className="h-5 w-5" />
          Upload Excel File
        </CardTitle>
        <CardDescription>
          Upload an Excel file with company data to start the research process
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div
          className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
            isDragging 
              ? 'border-primary bg-primary/5' 
              : 'border-muted-foreground/25 hover:border-primary/50'
          }`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
        >
          {selectedFile ? (
            <div className="space-y-4">
              <div className="flex items-center justify-center gap-3 text-lg">
                <FileSpreadsheet className="h-8 w-8 text-green-500" />
                <span className="font-medium">{selectedFile.name}</span>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setSelectedFile(null)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
              <p className="text-sm text-muted-foreground">
                {(selectedFile.size / 1024).toFixed(2)} KB
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              <FileSpreadsheet className="h-16 w-16 mx-auto text-muted-foreground" />
              <div>
                <p className="text-lg font-medium">Drop your Excel file here</p>
                <p className="text-sm text-muted-foreground">or click to browse</p>
              </div>
              <Button
                variant="outline"
                onClick={() => fileInputRef.current?.click()}
              >
                Select File
              </Button>
            </div>
          )}
          <input
            ref={fileInputRef}
            type="file"
            accept=".xlsx,.xls,.csv"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0]
              if (file) handleFileSelect(file)
            }}
          />
        </div>

        {selectedFile && (
          <Button
            className="w-full"
            size="lg"
            onClick={handleUpload}
            disabled={isUploading}
          >
            {isUploading ? (
              <>
                <div className="h-4 w-4 mr-2 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Uploading...
              </>
            ) : (
              <>
                <Upload className="h-4 w-4 mr-2" />
                Upload & Analyze
              </>
            )}
          </Button>
        )}

        <div className="text-sm text-muted-foreground space-y-1">
          <p className="font-medium">Supported formats:</p>
          <ul className="list-disc list-inside space-y-1">
            <li>Excel (.xlsx, .xls)</li>
            <li>CSV (.csv)</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  )
}

