import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Terminal, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useEffect, useRef } from 'react'

interface ConsoleLogEntry {
  timestamp: string
  level: 'INFO' | 'ERROR' | 'WARNING' | 'DEBUG'
  message: string
}

interface ConsoleLogProps {
  logs: ConsoleLogEntry[]
  onClear: () => void
}

export function ConsoleLog({ logs, onClear }: ConsoleLogProps) {
  const consoleEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    consoleEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'ERROR':
        return 'bg-red-500/10 text-red-500 border-red-500/20'
      case 'WARNING':
        return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20'
      case 'INFO':
        return 'bg-blue-500/10 text-blue-500 border-blue-500/20'
      case 'DEBUG':
        return 'bg-gray-500/10 text-gray-500 border-gray-500/20'
      default:
        return 'bg-gray-500/10 text-gray-500 border-gray-500/20'
    }
  }

  const getLevelBadgeVariant = (level: string): "default" | "destructive" | "outline" | "secondary" => {
    switch (level) {
      case 'ERROR':
        return 'destructive'
      case 'WARNING':
        return 'outline'
      case 'INFO':
        return 'default'
      default:
        return 'secondary'
    }
  }

  return (
    <Card className="h-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Terminal className="h-5 w-5" />
              Backend Console
            </CardTitle>
            <CardDescription>
              Live backend logs and activity
            </CardDescription>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={onClear}
            className="gap-2"
          >
            <Trash2 className="h-4 w-4" />
            Clear
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="bg-black/95 rounded-lg p-4 font-mono text-xs h-[600px] overflow-y-auto">
          {logs.length === 0 ? (
            <div className="text-gray-500 text-center py-8">
              No logs yet. Start using the application to see backend activity.
            </div>
          ) : (
            <div className="space-y-1">
              {logs.map((log, index) => (
                <div
                  key={index}
                  className={`p-2 rounded border ${getLevelColor(log.level)}`}
                >
                  <div className="flex items-start gap-2">
                    <Badge
                      variant={getLevelBadgeVariant(log.level)}
                      className="text-[10px] px-1.5 py-0 h-5 flex-shrink-0"
                    >
                      {log.level}
                    </Badge>
                    <span className="text-gray-400 flex-shrink-0 w-20">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </span>
                    <span className="text-gray-200 break-all flex-1">
                      {log.message}
                    </span>
                  </div>
                </div>
              ))}
              <div ref={consoleEndRef} />
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

