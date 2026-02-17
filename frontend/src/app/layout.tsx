import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "@/components/navbar";
import { QueryProvider } from "@/components/query-client-provider";
import { ThemeProvider } from "@/components/theme-provider";
import { Toaster } from "@/components/ui/sonner";
import { AuthProvider } from "@/providers/auth";

export const metadata: Metadata = {
  title: "BusLine",
  description: "BusLine passenger portal",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html suppressHydrationWarning lang="uk">
      <body>
        <ThemeProvider>
          <QueryProvider>
            <AuthProvider>
              <Navbar />
              {children}
            </AuthProvider>
          </QueryProvider>
          <Toaster richColors position="top-right" />
        </ThemeProvider>
      </body>
    </html>
  );
}
