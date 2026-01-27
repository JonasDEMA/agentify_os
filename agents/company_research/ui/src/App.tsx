/**
 * Company Research Agent - UI
 * Built with React + shadcn/ui
 */

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { 
  Upload, 
  Settings, 
  Search, 
  Download, 
  FileSpreadsheet,
  Building2,
  Users,
  TrendingUp,
  History,
  Newspaper,
  CheckCircle2,
  AlertCircle
} from 'lucide-react'

import { FileUpload } from '@/components/FileUpload'
import { FieldConfiguration } from '@/components/FieldConfiguration'
import { GapAnalysis } from '@/components/GapAnalysis'
import { ResearchProgress } from '@/components/ResearchProgress'
import { ResultsTable } from '@/components/ResultsTable'
import { ConsoleLog } from '@/components/ConsoleLog'
import * as api from '@/services/api'
import type { FieldConfig, GapAnalysisData, CompanyData, ConsoleLogEntry } from '@/services/api'

function App() {
  const [activeTab, setActiveTab] = useState('upload')
  const [gapAnalysis, setGapAnalysis] = useState<GapAnalysisData | null>(null)
  const [companies, setCompanies] = useState<CompanyData[]>([])
  const [isResearching, setIsResearching] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [fieldConfig, setFieldConfig] = useState<FieldConfig>({
    managing_directors: true,
    revenue: true,
    employees: true,
    history: false,
    news: false
  })
  const [jobId, setJobId] = useState<string | null>(null)
  const [researchProgress, setResearchProgress] = useState({
    progress: 0,
    total: 0,
    completed: 0,
    failed: 0,
    activityLog: [] as Array<{ timestamp: string; message: string }>
  })
  const [consoleLogs, setConsoleLogs] = useState<ConsoleLogEntry[]>([])

  // Poll console logs every 2 seconds
  useEffect(() => {
    const pollConsoleLogs = async () => {
      try {
        const result = await api.getConsoleLogs()
        if (result.success) {
          setConsoleLogs(result.logs)
        }
      } catch (err) {
        console.error('Failed to fetch console logs:', err)
      }
    }

    // Initial fetch
    pollConsoleLogs()

    // Poll every 2 seconds
    const interval = setInterval(pollConsoleLogs, 2000)

    return () => clearInterval(interval)
  }, [])

  const handleClearConsoleLogs = async () => {
    try {
      await api.clearConsoleLogs()
      setConsoleLogs([])
    } catch (err) {
      console.error('Failed to clear console logs:', err)
    }
  }

  const handleFileUpload = async (file: File) => {
    console.log('='.repeat(80))
    console.log('📤 FRONTEND: Starting file upload')
    console.log('File name:', file.name)
    console.log('File size:', file.size, 'bytes')
    console.log('File type:', file.type)

    setIsUploading(true)
    setError(null)

    try {
      console.log('🌐 FRONTEND: Calling API uploadExcel...')
      const result = await api.uploadExcel(file)
      console.log('✅ FRONTEND: API response received:', result)

      if (result.success) {
        console.log('✅ FRONTEND: Upload successful!')
        console.log('Gap analysis:', result.gap_analysis)
        console.log('Companies:', result.companies?.length || 0)

        setGapAnalysis(result.gap_analysis)
        setCompanies(result.companies)
        setActiveTab('analysis')

        console.log('✅ FRONTEND: State updated, switching to analysis tab')
      } else {
        console.error('❌ FRONTEND: Upload failed - success=false')
        setError('Upload failed. Please try again.')
      }
    } catch (err: any) {
      console.error('='.repeat(80))
      console.error('❌ FRONTEND: Upload error:', err)
      console.error('Error message:', err.message)
      console.error('Error response:', err.response?.data)
      console.error('Error status:', err.response?.status)
      console.error('='.repeat(80))

      setError(`Failed to upload file: ${err.response?.data?.detail || err.message}`)
    } finally {
      setIsUploading(false)
      console.log('='.repeat(80))
    }
  }

  const handleStartResearch = async () => {
    setIsResearching(true)
    setActiveTab('research')
    setError(null)

    try {
      // Configure fields first
      await api.configureFields(fieldConfig)

      // Start research
      const result = await api.startResearch()

      if (result.success) {
        setJobId(result.job_id)

        // Poll for progress
        const pollInterval = setInterval(async () => {
          try {
            const progressData = await api.getResearchProgress(result.job_id)

            // Update progress state
            setResearchProgress({
              progress: progressData.progress,
              total: progressData.total,
              completed: progressData.completed,
              failed: progressData.failed,
              activityLog: progressData.activity_log || []
            })

            if (progressData.status === 'completed') {
              clearInterval(pollInterval)

              // Get final results
              const resultsData = await api.getResearchResults(result.job_id)
              setCompanies(resultsData.results || [])
              setIsResearching(false)
              setActiveTab('results')
            } else if (progressData.status === 'error') {
              clearInterval(pollInterval)
              setError('Research failed. Please try again.')
              setIsResearching(false)
            }
          } catch (err) {
            console.error('Progress check failed:', err)
          }
        }, 2000) // Poll every 2 seconds
      }
    } catch (err) {
      console.error('Research failed:', err)
      setError('Failed to start research. Please try again.')
      setIsResearching(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      {/* Header */}
      <header className="border-b bg-white/50 dark:bg-slate-900/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-500 rounded-lg">
                <Building2 className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold">Company Research Agent</h1>
                <p className="text-sm text-muted-foreground">
                  Enrich your company data with web research
                </p>
              </div>
            </div>
            <Badge variant="outline" className="gap-1">
              <CheckCircle2 className="h-3 w-3" />
              v1.0.0
            </Badge>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-6 lg:w-[720px]">
            <TabsTrigger value="upload" className="gap-2">
              <Upload className="h-4 w-4" />
              Upload
            </TabsTrigger>
            <TabsTrigger value="config" className="gap-2">
              <Settings className="h-4 w-4" />
              Configure
            </TabsTrigger>
            <TabsTrigger value="analysis" className="gap-2" disabled={!gapAnalysis}>
              <AlertCircle className="h-4 w-4" />
              Analysis
            </TabsTrigger>
            <TabsTrigger value="research" className="gap-2" disabled={!gapAnalysis}>
              <Search className="h-4 w-4" />
              Research
            </TabsTrigger>
            <TabsTrigger value="results" className="gap-2" disabled={!gapAnalysis}>
              <Download className="h-4 w-4" />
              Results
            </TabsTrigger>
            <TabsTrigger value="console" className="gap-2">
              <Terminal className="h-4 w-4" />
              Console
            </TabsTrigger>
          </TabsList>

          {/* Error Display */}
          {error && (
            <Card className="border-red-200 bg-red-50 dark:bg-red-950/20">
              <CardContent className="pt-6">
                <div className="flex items-center gap-2 text-red-600 dark:text-red-400">
                  <AlertCircle className="h-5 w-5" />
                  <p>{error}</p>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Upload Tab */}
          <TabsContent value="upload" className="space-y-4">
            <FileUpload onFileUpload={handleFileUpload} isUploading={isUploading} />
          </TabsContent>

          {/* Configuration Tab */}
          <TabsContent value="config" className="space-y-4">
            <FieldConfiguration
              config={fieldConfig}
              onChange={setFieldConfig}
            />
          </TabsContent>

          {/* Gap Analysis Tab */}
          <TabsContent value="analysis" className="space-y-4">
            {gapAnalysis && (
              <GapAnalysis
                data={gapAnalysis}
                onStartResearch={handleStartResearch}
              />
            )}
          </TabsContent>

          {/* Research Tab */}
          <TabsContent value="research" className="space-y-4">
            <ResearchProgress
              isActive={isResearching}
              progress={researchProgress.progress}
              total={researchProgress.total}
              completed={researchProgress.completed}
              failed={researchProgress.failed}
              activityLog={researchProgress.activityLog}
            />
          </TabsContent>

          {/* Results Tab */}
          <TabsContent value="results" className="space-y-4">
            <ResultsTable companies={companies} jobId={jobId} />
          </TabsContent>

          {/* Console Tab */}
          <TabsContent value="console" className="space-y-4">
            <ConsoleLog logs={consoleLogs} onClear={handleClearConsoleLogs} />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}

export default App

