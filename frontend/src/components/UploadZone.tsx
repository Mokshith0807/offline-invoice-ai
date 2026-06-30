import { useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, File, X, Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { api } from '../services/api'

interface UploadZoneProps {
  onUploadComplete: () => void
}

export default function UploadZone({ onUploadComplete }: UploadZoneProps) {
  const [uploading, setUploading] = useState(false)
  const [files, setFiles] = useState<File[]>([])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'application/pdf': ['.pdf'],
    },
    maxSize: 50 * 1024 * 1024,
    onDrop: (accepted) => {
      setFiles((prev) => [...prev, ...accepted].slice(0, 5))
    },
  })

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index))
  }

  const uploadAll = async () => {
    if (files.length === 0) return
    setUploading(true)

    for (const file of files) {
      try {
        const result = await api.upload(file)
        if (result.status === 'completed') {
          toast.success(`${file.name} processed successfully`)
        } else {
          toast.error(`${file.name}: ${result.message}`)
        }
      } catch (e) {
        toast.error(`${file.name}: ${e instanceof Error ? e.message : 'Upload failed'}`)
      }
    }

    setFiles([])
    setUploading(false)
    onUploadComplete()
  }

  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all
          ${isDragActive
            ? 'border-blue-400 bg-blue-500/10'
            : 'border-dark-600 hover:border-dark-400 bg-dark-800/50 hover:bg-dark-800'
          }
        `}
      >
        <input {...getInputProps()} />
        <Upload className="w-12 h-12 mx-auto mb-4 text-dark-400" />
        {isDragActive ? (
          <p className="text-lg text-blue-400">Drop files here...</p>
        ) : (
          <div>
            <p className="text-lg text-dark-300">Drag & drop invoices here</p>
            <p className="text-sm text-dark-500 mt-1">JPG, PNG, PDF up to 50MB</p>
          </div>
        )}
      </div>

      {files.length > 0 && (
        <div className="space-y-2">
          {files.map((file, idx) => (
            <div key={idx} className="flex items-center gap-3 bg-dark-800 rounded-lg p-3">
              <File className="w-5 h-5 text-blue-400 shrink-0" />
              <span className="text-sm truncate flex-1">{file.name}</span>
              <span className="text-xs text-dark-500">{(file.size / 1024 / 1024).toFixed(1)}MB</span>
              <button onClick={() => removeFile(idx)} className="text-dark-500 hover:text-red-400">
                <X className="w-4 h-4" />
              </button>
            </div>
          ))}
          <button
            onClick={uploadAll}
            disabled={uploading}
            className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-dark-600 text-white rounded-lg font-medium flex items-center justify-center gap-2 transition-colors"
          >
            {uploading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Upload className="w-5 h-5" />
                Upload & Process ({files.length} file{files.length > 1 ? 's' : ''})
              </>
            )}
          </button>
        </div>
      )}
    </div>
  )
}
