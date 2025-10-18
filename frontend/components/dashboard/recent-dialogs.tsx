import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import type { RecentDialog } from "@/types/api";
import { formatRelativeTime } from "@/lib/format-utils";

interface RecentDialogsProps {
  dialogs: RecentDialog[];
  loading?: boolean;
}

function DialogSkeleton() {
  return (
    <div className="space-y-3">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="flex items-center justify-between gap-3 p-3 rounded-lg border">
          <div className="flex items-center gap-3">
            <Skeleton className="h-10 w-10 rounded-full" />
            <div className="space-y-2">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-3 w-20" />
            </div>
          </div>
          <Skeleton className="h-4 w-8" />
        </div>
      ))}
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex h-32 items-center justify-center">
      <p className="text-sm text-muted-foreground">No recent dialogs</p>
    </div>
  );
}

export function RecentDialogs({ dialogs, loading = false }: RecentDialogsProps) {
  if (loading) {
    return (
      <Card className="xl:col-span-2">
        <CardHeader className="flex flex-row items-center">
          <div className="grid gap-2">
            <CardTitle>Recent Dialogs</CardTitle>
            <CardDescription>Recent conversations with users</CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          <DialogSkeleton />
        </CardContent>
      </Card>
    );
  }

  if (!dialogs || dialogs.length === 0) {
    return (
      <Card className="xl:col-span-2">
        <CardHeader className="flex flex-row items-center">
          <div className="grid gap-2">
            <CardTitle>Recent Dialogs</CardTitle>
            <CardDescription>Recent conversations with users</CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          <EmptyState />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="xl:col-span-2">
      <CardHeader>
        <CardTitle>Recent Dialogs</CardTitle>
        <CardDescription>Recent conversations with users</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {dialogs.slice(0, 5).map((dialog) => (
            <div 
              key={dialog.user_id} 
              className="flex items-center justify-between p-3 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                  <span className="text-sm font-semibold text-primary">
                    {dialog.username.substring(0, 2).toUpperCase()}
                  </span>
                </div>
                <div>
                  <p className="text-sm font-medium">{dialog.username}</p>
                  <p className="text-xs text-muted-foreground">
                    {formatRelativeTime(dialog.last_activity)}
                  </p>
                </div>
              </div>
              <div className="text-sm font-medium">
                {dialog.messages_count}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
