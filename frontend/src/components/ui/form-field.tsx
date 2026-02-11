import React from "react";
import { Label } from "@/components/ui/label";

type FormFieldProps = {
	id: string;
	label: string;
	error?: string;
	className?: string;
	children: React.ReactNode;
};

export function FormField({ id, label, error, className, children }: FormFieldProps) {
	return (
		<div className={className ?? "space-y-2"}>
			<Label htmlFor={id}>{label}</Label>
			{children}
			{error && <p className="text-sm text-destructive">{error}</p>}
		</div>
	);
}
