import { Check, ChevronDown, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";

interface MultiSelectDropdownProps {
    label: string;
    placeholder: string;
    options: string[];
    selectedValues: string[];
    onChange: (values: string[]) => void;
    helperText?: string;
}

export default function MultiSelectDropdown({
    label,
    placeholder,
    options,
    selectedValues,
    onChange,
    helperText,
}: MultiSelectDropdownProps) {
    const [isOpen, setIsOpen] = useState(false);
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handleOutsideClick = (event: MouseEvent) => {
            if (!containerRef.current) return;
            if (containerRef.current.contains(event.target as Node)) return;
            setIsOpen(false);
        };

        document.addEventListener("mousedown", handleOutsideClick);
        return () => {
            document.removeEventListener("mousedown", handleOutsideClick);
        };
    }, []);

    const toggleValue = (value: string) => {
        const next = selectedValues.includes(value)
            ? selectedValues.filter((item) => item !== value)
            : [...selectedValues, value];
        onChange(next);
    };

    const removeValue = (value: string) => {
        onChange(selectedValues.filter((item) => item !== value));
    };

    return (
        <div ref={containerRef} className="relative grid gap-2">
            <p className="text-sm font-medium text-foreground">
                {label} {selectedValues.length > 0 ? `(${selectedValues.length})` : ""}
            </p>

            <button
                type="button"
                onClick={() => setIsOpen((previous) => !previous)}
                className="flex min-h-12 w-full items-center justify-between gap-3 rounded-xl border border-border/60 bg-card px-4 py-2 text-left text-sm shadow-sm transition-all hover:border-primary/50 hover:shadow-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
            >
                <div className="flex flex-1 flex-wrap items-center gap-2">
                    {selectedValues.length === 0 ? (
                        <span className="text-muted-foreground">{placeholder}</span>
                    ) : (
                        selectedValues.map((value) => (
                            <span
                                key={value}
                                className="inline-flex items-center gap-1 rounded-full border border-border bg-white px-2.5 py-1 text-xs font-medium text-foreground"
                            >
                                <span className="max-w-[170px] truncate">{value}</span>
                                <span
                                    role="button"
                                    tabIndex={0}
                                    onClick={(event) => {
                                        event.stopPropagation();
                                        removeValue(value);
                                    }}
                                    onKeyDown={(event) => {
                                        if (event.key === "Enter" || event.key === " ") {
                                            event.preventDefault();
                                            event.stopPropagation();
                                            removeValue(value);
                                        }
                                    }}
                                    className="ml-1 rounded-full p-0.5 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
                                >
                                    <X className="h-3 w-3" />
                                </span>
                            </span>
                        ))
                    )}
                </div>
                <ChevronDown className={`h-4 w-4 text-muted-foreground transition-transform ${isOpen ? "rotate-180" : ""}`} />
            </button>

            {isOpen ? (
                <div className="absolute left-0 right-0 top-[calc(100%+0.5rem)] z-30 max-h-64 overflow-y-auto rounded-xl border border-border/60 bg-card p-1 shadow-2xl backdrop-blur-xl">
                    {options.map((option) => {
                        const isSelected = selectedValues.includes(option);
                        return (
                            <button
                                key={option}
                                type="button"
                                onClick={() => toggleValue(option)}
                                className={`flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-left text-sm transition-colors font-medium ${isSelected
                                        ? "bg-primary/10 text-primary"
                                        : "text-foreground hover:bg-muted hover:text-foreground"
                                    }`}
                            >
                                <span className="truncate">{option}</span>
                                {isSelected ? <Check className="h-4 w-4" /> : null}
                            </button>
                        );
                    })}
                </div>
            ) : null}

            {helperText ? <p className="text-xs text-muted-foreground">{helperText}</p> : null}
        </div>
    );
}
