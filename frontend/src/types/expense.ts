export interface Expense {
  amount: number
  category: string
  subcategory?: string
  description: string
  date: string
  type: 'expense' | 'income'
  payment_method?: string
  confidence?: number
}