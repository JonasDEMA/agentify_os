import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Download, ExternalLink, CheckCircle2 } from 'lucide-react'
import type { CompanyData } from '@/services/api'
import * as api from '@/services/api'

interface ResultsTableProps {
  companies: CompanyData[]
  jobId: string | null
}

export function ResultsTable({ companies, jobId }: ResultsTableProps) {
  const handleExport = async () => {
    if (!jobId) {
      console.error('No job ID available')
      return
    }

    try {
      const blob = await api.exportResults(jobId)

      // Create download link
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `company_research_results_${new Date().toISOString().split('T')[0]}.xlsx`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      console.error('Export failed:', err)
    }
  }

  if (companies.length === 0) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-center text-muted-foreground">
            No results yet. Upload a file and start research to see results here.
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-green-500" />
                Enriched Company Data
              </CardTitle>
              <CardDescription>
                {companies.length} companies successfully researched
              </CardDescription>
            </div>
            <Button onClick={handleExport} disabled={!jobId}>
              <Download className="h-4 w-4 mr-2" />
              Export Excel
            </Button>
          </div>
        </CardHeader>
      </Card>

      {/* Results */}
      <div className="space-y-4">
        {companies.map((result, index) => (
          <Card key={index}>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-lg">{result.company_name}</CardTitle>
                  {result.website && (
                    <CardDescription className="flex items-center gap-2 mt-1">
                      <ExternalLink className="h-3 w-3" />
                      {result.website}
                    </CardDescription>
                  )}
                </div>
                {result.enriched && (
                  <Badge variant="default" className="gap-1">
                    <CheckCircle2 className="h-3 w-3" />
                    Enriched
                  </Badge>
                )}
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-xs font-medium text-muted-foreground mb-1">
                    Managing Directors
                  </p>
                  <p className="text-sm">{result.managing_directors}</p>
                </div>
                <div>
                  <p className="text-xs font-medium text-muted-foreground mb-1">
                    Revenue
                  </p>
                  <p className="text-sm font-semibold text-green-600">
                    {result.revenue}
                  </p>
                </div>
                <div>
                  <p className="text-xs font-medium text-muted-foreground mb-1">
                    Employees
                  </p>
                  <p className="text-sm">{result.employees}</p>
                </div>
                <div>
                  <p className="text-xs font-medium text-muted-foreground mb-1">
                    History
                  </p>
                  <p className="text-sm">{result.history}</p>
                </div>
                <div className="md:col-span-2">
                  <p className="text-xs font-medium text-muted-foreground mb-1">
                    Recent News
                  </p>
                  <p className="text-sm">{result.news}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Summary */}
      <Card className="bg-green-50 dark:bg-green-950/20 border-green-200 dark:border-green-800">
        <CardContent className="pt-6">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="h-8 w-8 text-green-500" />
            <div>
              <h3 className="font-semibold text-lg">Research Complete!</h3>
              <p className="text-sm text-muted-foreground">
                All companies have been successfully researched. You can now export the enriched data.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

