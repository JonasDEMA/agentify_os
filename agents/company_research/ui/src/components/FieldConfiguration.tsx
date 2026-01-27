import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import { Settings, Users, TrendingUp, History, Newspaper, Building2 } from 'lucide-react'

interface FieldConfig {
  managing_directors: boolean
  revenue: boolean
  employees: boolean
  history: boolean
  news: boolean
}

interface FieldConfigurationProps {
  config: FieldConfig
  onChange: (config: FieldConfig) => void
}

const fields = [
  {
    key: 'managing_directors' as keyof FieldConfig,
    label: 'Managing Directors',
    description: 'Names of company executives (Geschäftsführer)',
    icon: Users,
    color: 'text-blue-500'
  },
  {
    key: 'revenue' as keyof FieldConfig,
    label: 'Revenue',
    description: 'Company revenue/turnover (Umsatz)',
    icon: TrendingUp,
    color: 'text-green-500'
  },
  {
    key: 'employees' as keyof FieldConfig,
    label: 'Number of Employees',
    description: 'Total employee count (Anzahl Mitarbeiter)',
    icon: Building2,
    color: 'text-purple-500'
  },
  {
    key: 'history' as keyof FieldConfig,
    label: 'Company History',
    description: 'Brief company history and background',
    icon: History,
    color: 'text-orange-500'
  },
  {
    key: 'news' as keyof FieldConfig,
    label: 'Recent News',
    description: 'Current news and announcements',
    icon: Newspaper,
    color: 'text-red-500'
  }
]

export function FieldConfiguration({ config, onChange }: FieldConfigurationProps) {
  const handleToggle = (key: keyof FieldConfig) => {
    onChange({
      ...config,
      [key]: !config[key]
    })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Settings className="h-5 w-5" />
          Field Configuration
        </CardTitle>
        <CardDescription>
          Select which fields to extract from company websites
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {fields.map((field) => {
            const Icon = field.icon
            return (
              <div
                key={field.key}
                className="flex items-start space-x-3 p-4 rounded-lg border hover:bg-accent/50 transition-colors cursor-pointer"
                onClick={() => handleToggle(field.key)}
              >
                <Checkbox
                  checked={config[field.key]}
                  onCheckedChange={() => handleToggle(field.key)}
                  className="mt-1"
                />
                <div className="flex-1 space-y-1">
                  <div className="flex items-center gap-2">
                    <Icon className={`h-4 w-4 ${field.color}`} />
                    <label className="text-sm font-medium leading-none cursor-pointer">
                      {field.label}
                    </label>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {field.description}
                  </p>
                </div>
              </div>
            )
          })}
        </div>

        <div className="mt-6 p-4 bg-muted rounded-lg">
          <p className="text-sm font-medium mb-2">Selected Fields:</p>
          <div className="flex flex-wrap gap-2">
            {Object.entries(config)
              .filter(([_, enabled]) => enabled)
              .map(([key]) => {
                const field = fields.find(f => f.key === key)
                return field ? (
                  <span
                    key={key}
                    className="inline-flex items-center gap-1 px-2 py-1 bg-primary/10 text-primary rounded-md text-xs font-medium"
                  >
                    {field.label}
                  </span>
                ) : null
              })}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

