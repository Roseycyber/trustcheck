const CATEGORIES = [
  { value: 'job', label: 'Job' },
  { value: 'bank', label: 'Bank / payment' },
  { value: 'healthcare', label: 'Healthcare' },
  { value: 'brand', label: 'Brand / advert' },
  { value: 'other', label: 'Other' },
]

export default function CategoryTabs({ value, onChange }) {
  function handleKeyDown(event, categoryValue) {
    const currentIndex = CATEGORIES.findIndex((c) => c.value === categoryValue)
    let nextIndex = currentIndex

    if (event.key === 'ArrowRight') {
      nextIndex = (currentIndex + 1) % CATEGORIES.length
    } else if (event.key === 'ArrowLeft') {
      nextIndex = (currentIndex - 1 + CATEGORIES.length) % CATEGORIES.length
    } else {
      return
    }
    event.preventDefault()
    const nextValue = CATEGORIES[nextIndex].value
    onChange(nextValue)
    // Focus the next button after React re-renders
    const buttons = document.querySelectorAll('.category-tab')
    buttons[nextIndex]?.focus()
  }

  return (
    <div className="category-tabs" role="radiogroup" aria-label="What is this about?">
      {CATEGORIES.map((category) => {
        const isActive = category.value === value
        return (
          <button
            key={category.value}
            type="button"
            role="radio"
            aria-checked={isActive}
            tabIndex={isActive ? 0 : -1}
            className={`category-tab${isActive ? ' category-tab--active' : ''}`}
            onClick={() => onChange(category.value)}
            onKeyDown={(e) => handleKeyDown(e, category.value)}
          >
            {category.label}
          </button>
        )
      })}
    </div>
  )
}
