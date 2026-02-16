import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { PageContainer } from "@/components/ui/page-container";
import { routes } from "@/lib/routes";

const features = [
  {
    title: "Fast booking",
    description: "Book trips in minutes and manage orders online.",
  },
  {
    title: "Secure payments",
    description: "Modern payment methods with trusted carriers.",
  },
  {
    title: "Support 24/7",
    description: "We are here to help with any questions.",
  },
];

export default function HomePage() {
  return (
    <PageContainer centered={false} className="px-0 py-0">
      <section className="mx-auto flex max-w-6xl flex-col gap-10 px-6 py-16 lg:flex-row lg:items-center">
        <div className="flex-1 space-y-6">
          <p className="text-muted-foreground text-sm font-medium">
            BusLine · passenger portal
          </p>
          <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">
            Book bus trips quickly and confidently
          </h1>
          <p className="text-muted-foreground text-base sm:text-lg">
            Manage your tickets, view order history, and save favorite routes in
            one place.
          </p>
          <div className="flex flex-wrap gap-3">
            <Button asChild size="lg">
              <Link href={routes.register}>Create account</Link>
            </Button>
            <Button asChild variant="outline" size="lg">
              <Link href={routes.login}>Sign in</Link>
            </Button>
          </div>
        </div>
        <div className="grid flex-1 gap-4 sm:grid-cols-2">
          {features.map((feature) => (
            <Card key={feature.title} className="h-full">
              <CardHeader>
                <CardTitle>{feature.title}</CardTitle>
                <CardDescription>{feature.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <Button asChild variant="ghost" className="px-0">
                  <Link href={routes.register}>Learn more →</Link>
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>
    </PageContainer>
  );
}
