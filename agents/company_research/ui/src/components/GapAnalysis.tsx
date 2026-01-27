import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { AlertCircle, CheckCircle2, Search, TrendingUp } from 'lucide-react'

interface GapAnalysisData {
  total_companies: number
  complete_records: number
  incomplete_records: number
  missing_fields: Record<string, number>
}

interface GapAnalysisProps {
  data: GapAnalysisData
  onStartResearch: () => void
}

export function GapAnalysis({ data, onStartResearch }: GapAnalysisProps) {
  const completionRate = (data.complete_records / data.total_companies) * 100

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Total Companies</CardDescription>
            <CardTitle className="text-3xl">{data.total_companies}</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">
              Companies in uploaded file
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardDescription className="flex items-center gap-1">
              <CheckCircle2 className="h-3 w-3 text-green-500" />
              Complete Records
            </CardDescription>
            <CardTitle className="text-3xl text-green-600">
              {data.complete_records}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">
              {completionRate.toFixed(1)}% completion rate
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardDescription className="flex items-center gap-1">
              <AlertCircle className="h-3 w-3 text-orange-500" />
              Incomplete Records
            </CardDescription>
            <CardTitle className="text-3xl text-orange-600">
              {data.incomplete_records}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">
              Need research
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Completion Progress */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Data Completion
          </CardTitle>
          <CardDescription>
            Overall data completeness across all companies
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Completion Rate</span>
              <span className="font-medium">{completionRate.toFixed(1)}%</span>
            </div>
            <Progress value={completionRate} className="h-2" />
          </div>
        </CardContent>
      </Card>

      {/* Missing Fields Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5" />
            Missing Fields Analysis
          </CardTitle>
          <CardDescription>
            Number of companies missing each field
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {Object.entries(data.missing_fields).map(([field, count]) => {
              const percentage = (count / data.total_companies) * 100
              return (
                <div key={field} className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="font-medium capitalize">
                      {field.replace(/_/g, ' ')}
                    </span>
                    <span className="text-muted-foreground">
                      {count} / {data.total_companies} ({percentage.toFixed(0)}%)
                    </span>
                  </div>
                  <Progress value={percentage} className="h-1.5" />
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Action Button */}
      {data.incomplete_records > 0 && (
        <Card className="border-primary/50 bg-primary/5">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-semibold text-lg mb-1">
                  Ready to Start Research?
                </h3>
                <p className="text-sm text-muted-foreground">
                  The agent will research {data.incomplete_records} companies to fill in missing data
                </p>
              </div>
              <Button size="lg" onClick={onStartResearch}>
                <Search className="h-4 w-4 mr-2" />
                Start Research
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

