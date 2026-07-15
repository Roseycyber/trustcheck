const CATEGORIES = [
  { value: 'job', label: 'Job' },
  { value: 'bank', label: 'Bank / payment' },
  { value: 'healthcare', label: 'Healthcare' },
  { value: 'brand', label: 'Brand / advert' },
  { value: 'other', label: 'Other' },
]

export default function CategoryTabs({ value, onChange, ...rest }) {
  return (
    <div className="category-tabs" role="radiogroup" aria-label="What is this about?" {...rest}>
      {CATEGORIES.map((category) => {
        const isActive = category.value === value
        return (
          <button
            key={category.value}
            type="button"
            role="radio"
            aria-checked={isActive}
            className={`category-tab${isActive ? ' category-tab--active' : ''}`}
            onClick={() => onChange(category.value)}
          >
            {category.label}
          </button>
        )
      })}
    </div>
  )
}
