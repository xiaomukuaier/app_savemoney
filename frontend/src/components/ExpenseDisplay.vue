<template>
  <el-card class="expense-card" v-if="expense">
    <template #header>
      <div class="card-header">
        <span>记账信息确认</span>
        <el-tag :type="expense.confidence && expense.confidence > 0.8 ? 'success' : 'warning'">
          置信度: {{ Math.round((expense.confidence || 0.7) * 100) }}%
        </el-tag>
      </div>
    </template>

    <div class="expense-details">
      <div class="amount-section">
        <div class="amount">¥{{ expense.amount.toFixed(2) }}</div>
        <div class="type">{{ expense.type === 'expense' ? '支出' : '收入' }}</div>
      </div>

      <el-divider />

      <div class="detail-grid">
        <div class="detail-item">
          <label>分类:</label>
          <el-select v-model="localExpense.category" placeholder="选择分类">
            <el-option
              v-for="cat in categories"
              :key="cat"
              :label="cat"
              :value="cat"
            />
          </el-select>
        </div>

        <div class="detail-item">
          <label>子分类:</label>
          <el-select v-model="localExpense.subcategory" placeholder="选择子分类">
            <el-option
              v-for="subcat in getSubcategories(localExpense.category)"
              :key="subcat"
              :label="subcat"
              :value="subcat"
            />
          </el-select>
        </div>

        <div class="detail-item full-width">
          <label>描述:</label>
          <el-input
            v-model="localExpense.description"
            placeholder="请输入描述"
            clearable
          />
        </div>

        <div class="detail-item">
          <label>日期:</label>
          <el-date-picker
            v-model="localExpense.date"
            type="date"
            placeholder="选择日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </div>

        <div class="detail-item">
          <label>支付方式:</label>
          <el-select v-model="localExpense.payment_method" placeholder="选择支付方式">
            <el-option
              v-for="method in paymentMethods"
              :key="method"
              :label="method"
              :value="method"
            />
          </el-select>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="card-footer">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="handleConfirm">确认记账</el-button>
      </div>
    </template>
  </el-card>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { Expense } from '../types/expense'

const props = defineProps<{
  expense: Expense
}>()

const emit = defineEmits<{
  confirm: [expense: Expense]
  cancel: []
}>()

const localExpense = ref<Expense>({ ...props.expense })

// 分类数据
const categories = ['餐饮', '交通', '购物', '娱乐', '医疗', '其他']

const subcategories = {
  '餐饮': ['早餐', '午餐', '晚餐', '零食', '饮料'],
  '交通': ['地铁', '公交', '打车', '加油', '停车'],
  '购物': ['服装', '日用品', '电子产品', '书籍'],
  '娱乐': ['电影', '游戏', '旅游', '运动'],
  '医疗': ['药品', '检查', '治疗'],
  '其他': ['其他']
}

const paymentMethods = ['微信支付', '支付宝', '现金', '银行卡', '其他']

const getSubcategories = (category: string): string[] => {
  return subcategories[category as keyof typeof subcategories] || ['其他']
}

const handleConfirm = () => {
  emit('confirm', localExpense.value)
}

const handleCancel = () => {
  emit('cancel')
}

// 当分类变化时，重置子分类
watch(
  () => localExpense.value.category,
  (newCategory) => {
    const availableSubcategories = getSubcategories(newCategory)
    if (!availableSubcategories.includes(localExpense.value.subcategory || '')) {
      localExpense.value.subcategory = availableSubcategories[0]
    }
  }
)
</script>

<style scoped>
.expense-card {
  width: 400px;
  max-width: 90vw;
  margin-top: 2rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.amount-section {
  text-align: center;
  margin-bottom: 1rem;
}

.amount {
  font-size: 2.5rem;
  font-weight: bold;
  color: #f56c6c;
  margin-bottom: 0.5rem;
}

.type {
  font-size: 0.9rem;
  color: #909399;
}

.detail-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.detail-item.full-width {
  grid-column: 1 / -1;
}

.detail-item label {
  font-weight: 500;
  color: #606266;
  font-size: 0.9rem;
}

.card-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}
</style>