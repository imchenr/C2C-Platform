import dayjs from 'dayjs'

export const currency = (value) => `¥${Number(value || 0).toLocaleString('zh-CN')}`
export const dateTime = (value) => (value ? dayjs(value).format('YYYY-MM-DD HH:mm') : '—')
export const relativeTime = (value) => {
  if (!value) return ''
  const minutes = dayjs().diff(dayjs(value), 'minute')
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (minutes < 1440) return `${Math.floor(minutes / 60)}小时前`
  return dayjs(value).format('MM-DD')
}

export const statusMap = {
  pending: ['待付款', 'warning'],
  paid: ['已付款', 'primary'],
  meeting: ['待面交', 'primary'],
  completed: ['已完成', 'success'],
  cancelled: ['已取消', 'info'],
  refunding: ['退款中', 'warning'],
  refunded: ['已退款', 'info'],
  disputed: ['争议中', 'danger'],
  published: ['在售', 'success'],
  off_shelf: ['已下架', 'info'],
  rejected: ['已驳回', 'danger'],
  sold: ['已售出', 'info'],
  processing: ['处理中', 'primary'],
  resolved: ['已解决', 'success'],
  active: ['正常', 'success'],
  suspended: ['暂停', 'warning'],
  banned: ['封禁', 'danger'],
}

