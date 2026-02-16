import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const textVariants = cva("", {
  variants: {
    role: {
      h1: "text-4xl font-semibold tracking-tight sm:text-5xl",
      h2: "text-3xl font-semibold tracking-tight",
      h3: "text-2xl font-semibold",
      h4: "text-xl font-semibold",
      h5: "text-lg font-semibold",
      h6: "text-base font-semibold",
      p: "text-base text-foreground",
      "p-lg": "text-lg text-foreground",
      "p-sm": "text-sm text-foreground",
      "p-xs": "text-xs text-foreground",
      label: "text-sm font-medium",
      muted: "text-sm text-muted-foreground",
      "muted-xs": "text-xs text-muted-foreground",
      date: "text-xs text-muted-foreground",
      span: "text-foreground",
    },
  },
  defaultVariants: {
    role: "p",
  },
});

interface TextProps
  extends React.HTMLAttributes<HTMLElement>, VariantProps<typeof textVariants> {
  role?:
    | "h1"
    | "h2"
    | "h3"
    | "h4"
    | "h5"
    | "h6"
    | "p"
    | "p-lg"
    | "p-sm"
    | "p-xs"
    | "label"
    | "muted"
    | "muted-xs"
    | "date"
    | "span";
  asChild?: boolean;
}

const roleToElement: Record<string, keyof React.JSX.IntrinsicElements> = {
  h1: "h1",
  h2: "h2",
  h3: "h3",
  h4: "h4",
  h5: "h5",
  h6: "h6",
  p: "p",
  "p-lg": "p",
  "p-sm": "p",
  "p-xs": "p",
  label: "label",
  muted: "p",
  "muted-xs": "span",
  date: "p",
  span: "span",
};

const formatDate = (value: React.ReactNode) => {
  if (value instanceof Date) {
    return new Intl.DateTimeFormat(undefined, {
      year: "numeric",
      month: "short",
      day: "2-digit",
    }).format(value);
  }

  if (typeof value === "string" || typeof value === "number") {
    const parsed = new Date(value);
    if (!Number.isNaN(parsed.getTime())) {
      return new Intl.DateTimeFormat(undefined, {
        year: "numeric",
        month: "short",
        day: "2-digit",
      }).format(parsed);
    }
  }

  return value;
};

const Text = React.forwardRef<HTMLElement, TextProps>(
  ({ className, role = "p", ...props }, ref) => {
    const Component = roleToElement[role] as React.ElementType;
    return (
      <Component
        ref={ref}
        className={cn(textVariants({ role, className }))}
        {...props}
      >
        {role === "date" ? formatDate(props.children) : props.children}
      </Component>
    );
  },
);
Text.displayName = "Text";

export { Text, textVariants };
