# Metabase Native SQL Parameter Management - Technical Deep Dive

## Overview

When you create a native SQL query in Metabase with template tags like `{{limit}}`, the system automatically extracts these tags and creates corresponding parameters with UI controls. This document explains how this process works in both the frontend and backend, including the important distinction between template tags and parameters.

## Core Concepts: Template Tags vs Parameters

Before diving into the process, it's crucial to understand that Metabase uses two separate but interconnected data structures:

- **Template Tags**: SQL-level placeholders that exist within the query text and handle substitution during execution
- **Parameters**: UI-level interactive controls that collect user input and feed values to template tags

## The Automatic Parameter Creation Process

### 1. Template Tag Recognition

When you save a native SQL query like:
```sql
SELECT * FROM reporting.blended_performance LIMIT {{limit}}
```

**Backend Processing (Clojure):**
- The `metabase.lib.native/extract-template-tags` function uses regex patterns to find template tags in the SQL
- Three types of tags are recognized:
  - **Variable tags**: `{{variable_name}}` - for parameters
  - **Snippet tags**: `{{snippet: snippet_name}}` - for reusable SQL snippets  
  - **Card tags**: `{{#123}}` or `{{#123-card-title}}` - for referencing other questions

```clojure
(def ^:private variable-tag-regex
  #"\{\{\s*([A-Za-z0-9_\.]+)\s*\}\}")

(def ^:private snippet-tag-regex
  #"\{\{\s*(snippet:\s*[^}]+)\s*\}\}")

(def ^:private card-tag-regex
  #"\{\{\s*(#([0-9]*)(-[a-z0-9-]*)?)\s*\}\}")
```

### 2. Template Tag Creation and Type Assignment

**Initial Template Tag Creation:**
When a template tag is first discovered, Metabase creates a template tag object with **default settings**:

```clojure
(defn- fresh-tag [tag-name]
  {:type :text              ; ← ALL new tags default to :text
   :name tag-name
   :id   (str (random-uuid))})
```

**Key Point**: Template tag types are **NOT automatically inferred** from SQL context or variable names. All new template tags start as `:text` type, regardless of whether the variable is named `{{user_id}}`, `{{start_date}}`, or `{{limit}}`.

**Type Assignment Process:**
```clojure
(defn- finish-tag [{tag-name :name :as tag}]
  (merge tag
         ;; Check if it's a card reference like {{#123}}
         (when-let [card-id (tag-name->card-id tag-name)]
           {:type    :card
            :card-id card-id})
         ;; Check if it's a snippet like {{snippet: name}}
         (when-let [snippet-name (tag-name->snippet-name tag-name)]
           {:type         :snippet
            :snippet-name snippet-name})
         ;; Generate human-readable display name
         (when-not (:display-name tag)
           {:display-name (u.humanization/name->human-readable-name :simple tag-name)})))
```

**Available Template Tag Types:**
- **`:text`** → Default type for all variable tags
- **`:number`** → Must be manually set by user
- **`:date`** → Must be manually set by user  
- **`:dimension`** → Field filter type, manually set by user
- **`:snippet`** → Automatically assigned for `{{snippet: name}}` syntax
- **`:card`** → Automatically assigned for `{{#123}}` syntax

### 3. Parameter Creation from Template Tags

**Backend (metabase.queries.models.card/template-tag-parameters):**
This function transforms template tags into parameter objects for the UI:

```clojure
(defn template-tag-parameters
  "Transforms native query's `template-tags` into `parameters`."
  [card]
  (for [[_ {tag-type :type, widget-type :widget-type, :as tag}] 
        (get-in card [:dataset_query :native :template-tags])
        :when (and tag-type 
                   (or (contains? lib.schema.template-tag/raw-value-template-tag-types tag-type)
                       (and (= tag-type :dimension) widget-type (not= widget-type :none))))]
    {:id       (:id tag)
     :type     (or widget-type (cond (= tag-type :date)   :date/single
                                     (= tag-type :string) :string/=
                                     (= tag-type :number) :number/=
                                     :else                :category))  ; Default for :text
     :target   (if (= tag-type :dimension)
                 [:dimension [:template-tag (:name tag)]]
                 [:variable  [:template-tag (:name tag)]])
     :name     (:display-name tag)
     :slug     (:name tag)
     :default  (:default tag)
     :required (boolean (:required tag))}))
```

**Frontend (TypeScript):**
The equivalent logic exists in `frontend/src/metabase-lib/v1/parameters/utils/template-tags.ts`:

```typescript
function getParameterType(tag: TemplateTag) {
  if (tag["widget-type"]) {
    return tag["widget-type"];  // User-specified override
  }

  const { type } = tag;
  if (type === "date") {
    return "date/single";
  }
  if (type === "string") {     // Legacy support
    return "string/=";
  }
  if (type === "number") {     // Legacy support  
    return "number/=";
  }
  return "category";           // Default for :text type
}

export function getTemplateTagParameter(
  tag: TemplateTag,
  config?: ParameterValuesConfig,
): ParameterWithTarget {
  return {
    id: tag.id,
    type: getParameterType(tag),
    target: getParameterTarget(tag),
    name: tag["display-name"],
    slug: tag.name,
    default: tag.default,
    required: tag.required,
    options: tag.options,
    // ... additional config
  };
}
```

### 4. The Card Save Flow

When you hit "Save" on a native query:

1. **Frontend sends POST to `/api/question`** with:
   ```json
   {
     "name": "Manual param test",
     "dataset_query": {
       "database": 195,
       "type": "native",
       "native": {
         "template-tags": {
           "limit": {
             "type": "text",
             "name": "limit", 
             "id": "b9d76a9e-46b7-4c73-a6d6-3645384cbf78",
             "display-name": "Limit"
           }
         },
         "query": "SELECT * FROM reporting.blended_performance LIMIT {{limit}}"
       }
     },
     "parameters": [
       {
         "id": "b9d76a9e-46b7-4c73-a6d6-3645384cbf78",
         "type": "category",
         "target": ["variable", ["template-tag", "limit"]],
         "name": "Limit",
         "slug": "limit"
       }
     ]
   }
   ```

2. **Backend processing in `metabase.queries.api.card/POST`:**
   - Validates the query
   - Extracts template tags automatically using `extract-template-tags`
   - Creates parameter objects from template tags using `template-tag-parameters`
   - Stores the card with both template tags and parameters in the database

## The Relationship: Template Tags vs Parameters

### Two Views of the Same Concept

Template tags and parameters represent the same concept from different perspectives:

- **Template Tags** (SQL layer): Define placeholders in SQL text that need substitution
- **Parameters** (UI layer): Provide interactive controls for collecting user input

### Data Flow
```
User Input → Parameter → Template Tag → SQL Substitution → Query Execution
     ↓            ↓           ↓             ↓                ↓
  UI Widget → Collect Value → Find Tag → Replace {{}} → Run Query
```

### Linking Mechanism
Parameters connect to template tags through the `target` field:
```clojure
{:target ["variable" ["template-tag" "limit"]]}
```

This creates the bridge between UI parameter and SQL template tag.

### Why Two Separate Structures?

1. **Separation of Concerns**: Template tags handle SQL mechanics, parameters handle UI/UX
2. **Different Lifecycles**: Template tags change when SQL changes, parameters can be customized independently
3. **Dashboard Integration**: Dashboard parameters can map to template tags across multiple cards
4. **Flexibility**: Multiple parameters can target the same template tag with different UI configurations

## Data Structures

### Template Tag Structure

Template tags are stored in the `dataset_query.native.template-tags` object with this structure:

```clojure
{:template-tags 
 {"limit" {:type "text"           ; Always starts as "text", user can change
           :name "limit"          ; tag name from {{limit}}
           :id "uuid-string"      ; unique identifier linking to parameter
           :display-name "Limit"  ; human-readable name
           :default nil           ; optional default value
           :required false        ; whether required
           :widget-type nil}}}    ; optional UI widget override
```

### Parameter Structure

Parameters are stored in the card's `parameters` array:

```clojure
[{:id "uuid-string"              ; Links to template tag ID
  :type "category"               ; UI widget type (converted from template tag)
  :target ["variable" ["template-tag" "limit"]]  ; Links to template tag
  :name "Limit"                  ; UI label
  :slug "limit"                  ; URL-friendly name
  :default nil                   ; Default UI value
  :required false                ; UI validation
  :values_query_type "list"      ; How to populate values
  :values_source_config {...}}]  ; Value source configuration
```

## Type System and User Customization

### Default Type Assignment

| Template Tag Type | Parameter Type | UI Widget | When Assigned |
|-------------------|----------------|-----------|---------------|
| `text` | `category` | Text input with autocomplete | **Default for all variable tags** |
| `number` | `number/=` | Number input | User manually changes type |
| `date` | `date/single` | Date picker | User manually changes type |
| `dimension` | Based on field | Field-specific widget | User selects "Field Filter" |
| `snippet` | N/A | N/A | Auto-assigned for `{{snippet: name}}` |
| `card` | N/A | N/A | Auto-assigned for `{{#123}}` |

### Manual Type Customization

Users can change template tag types through the **Variable Settings sidebar**:

```typescript
// From TagEditorParam.tsx
setType = (type: TemplateTagType) => {
  if (tag.type !== type) {
    setTemplateTag({
      ...tag,
      type: type,
      default: undefined,
      dimension: undefined,
      "widget-type": type === "dimension" ? "none" : undefined,
    });
  }
};
```

### Smart Field Filters

When users select "Field Filter" type (`dimension`):
1. System prompts for database field selection
2. Analyzes selected field characteristics  
3. Suggests optimal parameter widget based on field metadata:

```typescript
export function getDefaultParameterWidgetType(tag: TemplateTag, field: Field) {
  const distinctCount = field.fingerprint?.global?.["distinct-count"];
  
  if (distinctCount != null && distinctCount > 20 && 
      options.some(option => option.type === "string/contains")) {
    return "string/contains";  // High-cardinality → "contains" filter
  }
  
  return options[0].type;      // Otherwise, first valid option
}
```

## Real-World Examples

### Example 1: Default Text Parameter
```sql
SELECT * FROM users WHERE status = {{user_status}}
```

**Automatic Processing:**
1. Parser finds `{{user_status}}`
2. Creates template tag: `{type: "text", name: "user_status", id: "uuid1"}`
3. Creates parameter: `{type: "category", target: ["variable", ["template-tag", "user_status"]]}`
4. UI renders: Text input with autocomplete

### Example 2: User Customizes to Number
**User Action:** Opens Variable Settings → Changes type to "Number"

**Result:**
- Template tag becomes: `{type: "number", name: "user_status"}`
- Parameter becomes: `{type: "number/=", ...}`
- UI renders: Number input field

### Example 3: Field Filter
```sql
SELECT * FROM orders WHERE {{date_filter}}
```

**User Action:** Changes type to "Field Filter" → Selects `orders.created_at` field

**Result:**
- Template tag: `{type: "dimension", dimension: ["field", 123, null], widget-type: "date/all-options"}`
- Parameter: `{type: "date/all-options", target: ["dimension", ["template-tag", "date_filter"]]}`
- UI renders: Advanced date picker with relative date options

### Example 4: The POST Request

When saving the card, the frontend sends both structures:

```json
{
  "dataset_query": {
    "native": {
      "template-tags": {
        "limit": {
          "type": "text",
          "name": "limit", 
          "id": "b9d76a9e-46b7-4c73-a6d6-3645384cbf78",
          "display-name": "Limit"
        }
      },
      "query": "SELECT * FROM reporting.blended_performance LIMIT {{limit}}"
    }
  },
  "parameters": [
    {
      "id": "b9d76a9e-46b7-4c73-a6d6-3645384cbf78",
      "type": "category",
      "target": ["variable", ["template-tag", "limit"]],
      "name": "Limit",
      "slug": "limit"
    }
  ]
}
```

## Architecture and Implementation

### Frontend Parameter Management

**Key Files:**
- `frontend/src/metabase-lib/v1/parameters/utils/template-tags.ts` - Parameter conversion logic
- `frontend/src/metabase/query_builder/components/NativeQueryEditor/` - Native editor UI
- `frontend/src/metabase/query_builder/components/ResponsiveParametersList/` - Parameter UI widgets
- `frontend/src/metabase/query_builder/components/template_tags/TagEditorParam.tsx` - Variable settings UI

**Parameter UI Generation:**
The frontend automatically generates parameter input widgets based on the parameter type:
- `category` → Text input with auto-complete (default for `:text` template tags)
- `string/=` → Dropdown or text input
- `number/=` → Number input
- `date/single` → Date picker
- `dimension` types → Field-specific widgets (dropdowns, date pickers, etc.)

### Backend Query Processing
**During Query Execution:**
1. `metabase.query-processor.middleware.parameters.native/expand-inner` processes parameters
2. Template tags are replaced with actual values or SQL fragments
3. The driver-specific parameter substitution occurs (SQL placeholders, etc.)

**Parameter Validation:**
- `metabase.parameters.params/assert-valid-parameters` validates parameter structure
- Field filters check that referenced fields belong to the correct database
- Circular reference detection for card-type template tags

### Lifecycle Hooks

**Card Creation (`pre-insert`):**
- Extract template tags from query using `extract-template-tags`
- Generate parameter objects using `template-tag-parameters` if missing
- Validate field filters point to correct database
- Check for circular references in card-type template tags

**Card Updates (`pre-update`):**
- Re-extract template tags if query changed
- Update Field Values for On-Demand databases
- Validate parameter mappings
- Update dependent dashboard parameters

## Advanced Features

**Field Filters (Dimension Type):**
Template tags of type "dimension" create powerful field filters that can:
- Reference specific table columns
- Generate appropriate SQL WHERE clauses
- Support various operators (=, !=, contains, etc.)
- Provide value suggestions from the field

**Parameter Dependencies:**
Parameters can be linked to create cascading filters where one parameter's values depend on another's selection.

**Dashboard Integration:**
Parameters from native queries can be mapped to dashboard parameters, allowing filtering across multiple cards.

## Schema Evolution

Metabase uses a schema versioning system (`card_schema` column) to handle parameter format changes:
- Current schema version: 22
- Automatic upgrades during card selection
- Backward compatibility for older formats

## Key Takeaways

1. **Dual Structure Design**: Template tags handle SQL substitution, parameters handle UI interaction - both are necessary and complementary

2. **No Magic Type Inference**: Template tag types are **not** automatically inferred from SQL context or variable names - all start as `:text` type

3. **User-Driven Customization**: Users explicitly choose parameter types through the Variable Settings sidebar for optimal UX

4. **Automatic Creation**: The system creates both template tags and parameters without manual configuration, but with sensible defaults

5. **Smart Field Filters**: When using dimension type, the system analyzes database field metadata to suggest optimal parameter widgets

6. **Frontend-Backend Sync**: Both sides maintain consistent parameter extraction and conversion logic

7. **Dashboard Integration**: Parameters enable cross-card filtering and dashboard-level parameter mapping

8. **Extensible Design**: The system supports various parameter types and UI widgets while maintaining SQL power

This dual-structure approach makes Metabase's native query editor both user-friendly and powerful, providing the flexibility of raw SQL with the convenience of interactive parameters, while ensuring predictable behavior through explicit user control rather than potentially incorrect automatic inference.