import { config } from "dotenv";
import { defineConfig } from "orval";

config({ path: ".env.local" });

const API_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export default defineConfig({
	main: {
		input: `${API_URL}/openapi.json`,
		output: {
			mode: "tags-split",
			target: "./src/generated/api/endpoints",
			schemas: "./src/generated/api/model",
			client: "react-query",
			httpClient: "axios",
			clean: true,
			override: {
				mutator: {
					path: "./src/lib/api/http-instance.ts",
					name: "httpInstance",
				},
				operationName: (operation, route, verb) => {
					const summary = operation.summary || operation.operationId || route;

					let pascalName = summary
						.replace(/[/_{}-]/g, " ")
						.split(" ")
						.filter(Boolean)
						.map((word: string) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
						.join("");

					const commonVerbs = ["Get", "Post", "Put", "Delete", "Patch", "Create", "Update"];

					commonVerbs.forEach((v) => {
						if (pascalName.startsWith(v)) {
							pascalName = pascalName.slice(v.length);
						}
					});

					return `${verb.toLowerCase()}${pascalName}`;
				},
			},
		},
	},
});
