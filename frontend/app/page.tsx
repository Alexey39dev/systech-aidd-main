import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="container mx-auto px-4 py-16">
        <div className="mb-12 text-center">
          <h1 className="mb-4 text-4xl font-bold text-slate-900">Systech AI Assistant</h1>
          <p className="mb-8 text-xl text-slate-600">
            Monitoring and analytics dashboard for AI conversations
          </p>
          <div className="flex justify-center gap-4">
            <Link href="/dashboard">
              <Button size="lg">Open Dashboard</Button>
            </Link>
            <Link href="/doc/api-specification">
              <Button variant="outline" size="lg">API Documentation</Button>
            </Link>
          </div>
        </div>

        <div className="mx-auto grid max-w-4xl gap-6 md:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle>Real-time Analytics</CardTitle>
              <CardDescription>Monitor conversation metrics and user activity</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-slate-600">
                Track total dialogs, active users, and conversation patterns with interactive charts
                and visualizations.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>User Insights</CardTitle>
              <CardDescription>Understand user behavior and engagement</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-slate-600">
                Analyze top users, recent conversations, and engagement trends to optimize AI
                assistant performance.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Performance Metrics</CardTitle>
              <CardDescription>Monitor system performance and response times</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-slate-600">
                Track response times, error rates, and system health to ensure optimal user
                experience.
              </p>
            </CardContent>
          </Card>
        </div>

        <div className="mt-12 text-center">
          <p className="text-slate-500">Built with Next.js 15, TypeScript, and shadcn/ui</p>
        </div>
      </div>
    </div>
  );
}
