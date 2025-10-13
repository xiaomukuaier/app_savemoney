export interface Expense {
  amount: number
  category: string
  subcategory?: string
  description: string
  date: string
  type: 'expense' | 'income'
  payment_method?: string
  confidence?: number
  is_daily?: string
  is_necessary?: string
  raw_text?: string
}