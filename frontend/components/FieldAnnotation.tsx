"use client";

interface Field {
  field_name: string;
  field_type: string;
  suggested_value?: string | null;
  instructions: string;
  warning?: string | null;
  position?: { x: number; y: number } | null;
}

interface FieldAnnotationProps {
  field: Field;
  index: number;
}

const FIELD_TYPE_LABELS: Record<string, string> = {
  text: "Text",
  email: "Email",
  date: "Date",
  tel: "Phone",
  number: "Number",
  select: "Dropdown",
  checkbox: "Checkbox",
  radio: "Radio",
  textarea: "Long text",
  password: "Password",
  url: "URL",
  file: "File upload",
};

export default function FieldAnnotation({ field, index }: FieldAnnotationProps) {
  const typeLabel = FIELD_TYPE_LABELS[field.field_type] ?? field.field_type;

  return (
    <div className="group relative rounded-lg border border-slate-200 bg-white p-4 shadow-sm hover:shadow-md transition-shadow duration-200">
      {/* Header row */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-center gap-2 min-w-0">
          <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-600 text-white text-xs font-bold flex items-center justify-center">
            {index + 1}
          </span>
          <h3 className="text-sm font-semibold text-slate-800 truncate">{field.field_name}</h3>
        </div>
        <span className="flex-shrink-0 text-xs font-medium text-blue-700 bg-blue-50 border border-blue-200 rounded-full px-2 py-0.5">
          {typeLabel}
        </span>
      </div>

      {/* Suggested value */}
      {field.suggested_value && (
        <div className="mb-3 rounded-md bg-green-50 border border-green-200 px-3 py-2">
          <p className="text-xs text-green-700 font-medium mb-0.5">Suggested value</p>
          <p className="text-sm text-green-900 font-mono">{field.suggested_value}</p>
        </div>
      )}

      {/* Instructions */}
      <p className="text-sm text-slate-600 leading-relaxed">{field.instructions}</p>

      {/* Warning */}
      {field.warning && (
        <div className="mt-3 rounded-md bg-amber-50 border border-amber-200 px-3 py-2 flex gap-2">
          <svg
            className="w-4 h-4 text-amber-500 flex-shrink-0 mt-0.5"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
          <p className="text-xs text-amber-800">{field.warning}</p>
        </div>
      )}
    </div>
  );
}
