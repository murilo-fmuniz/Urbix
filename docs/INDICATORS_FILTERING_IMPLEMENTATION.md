# ISO Category Filtering Implementation - IndicatorsComparisonChart

## Summary of Changes

### Component: `IndicatorsComparisonChart.jsx`

#### 1. **State Management (Added)**
```javascript
const [selectedCategories, setSelectedCategories] = useState(
  new Set(['iso_37120', 'iso_37122', 'iso_37123'])
);
```
- Tracks which ISO categories are selected
- Default: All categories selected (37120, 37122, 37123)
- Uses Set for efficient lookups

#### 2. **Helper Functions (Added)**
```javascript
// Determines category based on indicator index
const getIndicatorCategory = (index) => {
  if (index < 18) return 'iso_37120'; // 18 indicators
  if (index < 34) return 'iso_37122'; // 16 indicators
  return 'iso_37123'; // 16 indicators
};

// Category metadata for UI display
const CATEGORY_INFO = {
  iso_37120: { label: 'ISO 37120 (Finanças, Governança)', color: '#ff9800', ... },
  iso_37122: { label: 'ISO 37122 (Tecnologia, Energia)', color: '#9c27b0', ... },
  iso_37123: { label: 'ISO 37123 + Sendai (Resiliência, Saúde)', color: '#2196f3', ... },
};
```

#### 3. **Filter Toggle Functions (Added)**
```javascript
const toggleCategory = (category) => {
  // Toggles individual category on/off
};

const selectAllCategories = () => {
  // Selects all three categories
};

const deselectAllCategories = () => {
  // Deselects all categories (shows warning)
};
```

#### 4. **Dynamic Data Filtering (Added)**
```javascript
const filteredData = useMemo(() => {
  // Filter indicators based on selected categories
  // Update chart and table data accordingly
  // Returns only data for selected ISO categories
}, [cidades, matrizDecisao, indicadores, selectedCategories]);
```

#### 5. **UI Filter Section (Added)**
```jsx
<div className="iso-filter-section">
  <div className="filter-header">
    <h4>🏷️ Filtrar por Categoria ISO</h4>
    <div className="filter-buttons">
      <button onClick={selectAllCategories}>✓ Todas</button>
      <button onClick={deselectAllCategories}>✗ Nenhuma</button>
    </div>
  </div>

  <div className="filter-checkboxes">
    {/* Three checkboxes for ISO 37120, 37122, 37123 */}
  </div>
</div>
```

### Styles: `IndicatorsComparisonChart.css` (Added)

#### New Classes:
- `.iso-filter-section` - Container with gradient background and border
- `.filter-header` - Header with title and quick-select buttons
- `.filter-buttons` - Styling for "Todas" and "Nenhuma" buttons
- `.filter-checkboxes` - Grid layout for checkbox options
- `.filter-checkbox` - Individual checkbox styling with hover effects
- `.filter-btn-small` - Quick action button styling

---

## Features Implemented

### ✅ **Multi-Select Filtering**
- Users can toggle any combination of ISO categories
- Checkboxes allow granular control
- Default: All categories selected

### ✅ **Quick Actions**
- "✓ Todas" button - Selects all categories
- "✗ Nenhuma" button - Deselects all (shows warning message)

### ✅ **Dynamic Chart Updates**
- Chart automatically filters when categories change
- Title shows filtered indicator count: "Comparação... (32 indicadores)"
- Only selected categories' data rendered

### ✅ **Dynamic Table Updates**
- Table columns filtered to show only selected indicators
- Indicator headers include ISO category (via title tooltip)
- Values properly aligned with filtered data

### ✅ **User Feedback**
- Empty state: "⚠️ Selecione pelo menos uma categoria ISO"
- Checkbox labels show indicator count per category: "(18)", "(16)", "(16)"
- Visual indicators: colors and borders for each category

---

## User Experience Flow

1. **View Comparison** - Chart shows all 50 indicators by default
2. **Select Category** - User checks/unchecks ISO categories
3. **See Results** - Chart and table dynamically update to filtered data
4. **Quick Control** - "Todas" and "Nenhuma" buttons for rapid selection

---

## Technical Implementation

### Data Flow:
```
User selects category
       ↓
toggleCategory() updates state
       ↓
filteredData useMemo recomputes with filter
       ↓
Indices determined by getIndicatorCategory()
       ↓
Chart and Table re-rendered with filtered data
       ↓
Display shows only selected ISO categories
```

### Performance:
- `useMemo` prevents unnecessary recalculations
- Filtering done on index positions (O(n) complexity)
- Set data structure for O(1) category lookups

---

## Browser Compatibility

✅ Modern browsers (Chrome, Firefox, Safari, Edge)
✅ Mobile-friendly responsive design
✅ Keyboard accessible (checkboxes with labels)

---

## Future Enhancements

1. Add indicator search/filter by name
2. Save filter preferences to localStorage
3. Export filtered chart data to CSV
4. Add indicator tooltips with descriptions
5. Comparison with historical data for same categories
