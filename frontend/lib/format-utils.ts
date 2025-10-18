/**
 * Форматирует число с разделителями тысяч
 * @param value - число для форматирования
 * @returns отформатированная строка (например, "1,247")
 */
export function formatNumber(value: number): string {
  return new Intl.NumberFormat('ru-RU').format(value);
}

/**
 * Форматирует дату в зависимости от периода
 * @param date - дата в ISO формате
 * @param period - период отображения
 * @returns отформатированная дата
 */
export function formatDate(date: string, period: 'day' | 'week' | 'month'): string {
  const parsedDate = new Date(date);
  
  switch (period) {
    case 'day':
      // Для дня показываем только часы: "14:00"
      return parsedDate.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
    case 'week':
      // Для недели показываем день недели и дату: "Mon 17"
      return parsedDate.toLocaleDateString('ru-RU', { weekday: 'short', day: 'numeric' });
    case 'month':
      // Для месяца показываем месяц и день: "Oct 17"
      return parsedDate.toLocaleDateString('ru-RU', { month: 'short', day: 'numeric' });
    default:
      return parsedDate.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' });
  }
}

/**
 * Форматирует дату в относительное время
 * @param date - дата в ISO формате
 * @returns относительное время (например, "2 minutes ago")
 */
export function formatRelativeTime(date: string): string {
  const parsedDate = new Date(date);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - parsedDate.getTime()) / 1000);
  
  if (diffInSeconds < 60) {
    return 'только что';
  } else if (diffInSeconds < 3600) {
    const minutes = Math.floor(diffInSeconds / 60);
    return `${minutes} мин назад`;
  } else if (diffInSeconds < 86400) {
    const hours = Math.floor(diffInSeconds / 3600);
    return `${hours} ч назад`;
  } else {
    const days = Math.floor(diffInSeconds / 86400);
    return `${days} дн назад`;
  }
}

/**
 * Форматирует процентное значение
 * @param value - числовое значение процента
 * @returns отформатированная строка с символом %
 */
export function formatPercentage(value: number): string {
  return `${value > 0 ? '+' : ''}${value.toFixed(1)}%`;
}

/**
 * Форматирует timestamp для графика в зависимости от периода
 * @param timestamp - timestamp в ISO формате
 * @param period - период отображения
 * @returns отформатированная строка для оси X
 */
export function formatTimestamp(timestamp: string, period: 'day' | 'week' | 'month'): string {
  return formatDate(timestamp, period);
}
