import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Search, CheckCircle2, Clock, Globe, XCircle } from 'lucide-react'

interface ActivityLogEntry {
  timestamp: string
  message: string
}

interface ResearchProgressProps {
  isActive: boolean
  progress: number
  total: number
  completed: number
  failed: number
  activityLog: ActivityLogEntry[]
}

export function ResearchProgress({
  isActive,
  progress,
  total,
  completed,
  failed,
  activityLog
}: ResearchProgressProps) {
  const processedCount = completed + failed

  return (
    <div className="space-y-6">
      {/* Overall Progress */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Research Progress
          </CardTitle>
          <CardDescription>
            Researching company information from websites
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Overall Progress</span>
              <span className="font-medium">
                {processedCount} / {totalCount} companies
              </span>
            </div>
            <Progress value={progress} className="h-3" />
            <p className="text-xs text-muted-foreground">
              {progress.toFixed(0)}% complete
            </p>
          </div>

          {isActive && activityLog.length > 0 && (
            <div className="p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg border border-blue-200 dark:border-blue-800">
              <div className="flex items-center gap-2 mb-2">
                <Globe className="h-4 w-4 text-blue-500 animate-pulse" />
                <span className="text-sm font-medium">Latest activity:</span>
              </div>
              <p className="text-sm text-muted-foreground">
                {activityLog[activityLog.length - 1]?.message || 'Processing...'}
              </p>
            </div>
          )}

          {!isActive && processedCount === total && (
            <div className="p-4 bg-green-50 dark:bg-green-950/20 rounded-lg border border-green-200 dark:border-green-800">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-500" />
                <span className="text-sm font-medium">Research completed!</span>
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                {completed} successful, {failed} failed
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Activity Log */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Activity Log
          </CardTitle>
          <CardDescription>
            Recent research activities
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {activityLog.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-4">
                No activity yet. Start research to see progress.
              </p>
            ) : (
              activityLog.slice().reverse().map((item, index) => {
                const isSuccess = item.message.includes('✅') || item.message.includes('Completed')
                const isFailed = item.message.includes('❌') || item.message.includes('Failed') || item.message.includes('Skipped')
                const isProcessing = item.message.includes('Researching') || item.message.includes('Processing')

                return (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 rounded-lg border"
                  >
                    <div className="flex items-center gap-3">
                      {isSuccess ? (
                        <CheckCircle2 className="h-4 w-4 text-green-500 flex-shrink-0" />
                      ) : isFailed ? (
                        <XCircle className="h-4 w-4 text-red-500 flex-shrink-0" />
                      ) : isProcessing ? (
                        <div className="h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin flex-shrink-0" />
                      ) : (
                        <Clock className="h-4 w-4 text-gray-500 flex-shrink-0" />
                      )}
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{item.message}</p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(item.timestamp).toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                    <Badge
                      variant={isSuccess ? 'default' : isFailed ? 'destructive' : 'secondary'}
                      className="flex-shrink-0"
                    >
                      {isSuccess ? 'Complete' : isFailed ? 'Failed' : 'Processing'}
                    </Badge>
                  </div>
                )
              })
            )}
          </div>
        </CardContent>
      </Card>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Completed</CardDescription>
            <CardTitle className="text-2xl text-green-600">{completed}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Failed</CardDescription>
            <CardTitle className="text-2xl text-red-600">{failed}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Total Companies</CardDescription>
            <CardTitle className="text-2xl">{total}</CardTitle>
          </CardHeader>
        </Card>
      </div>
    </div>
  )
}

