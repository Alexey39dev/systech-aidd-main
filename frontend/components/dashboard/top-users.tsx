import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import type { TopUser } from "@/types/api";

interface TopUsersProps {
  users: TopUser[];
  loading?: boolean;
}

function UserSkeleton() {
  return (
    <div className="space-y-3">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="flex items-center gap-3 p-3 rounded-lg border">
          <Skeleton className="h-10 w-10 rounded-full" />
          <div className="space-y-2 flex-1">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-3 w-32" />
          </div>
        </div>
      ))}
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex h-32 items-center justify-center">
      <p className="text-sm text-muted-foreground">No users data</p>
    </div>
  );
}

export function TopUsers({ users, loading = false }: TopUsersProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Top Active Users</CardTitle>
          <CardDescription>Users ranked by message count</CardDescription>
        </CardHeader>
        <CardContent>
          <UserSkeleton />
        </CardContent>
      </Card>
    );
  }

  if (!users || users.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Top Active Users</CardTitle>
          <CardDescription>Users ranked by message count</CardDescription>
        </CardHeader>
        <CardContent>
          <EmptyState />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Top Active Users</CardTitle>
        <CardDescription>Users ranked by message count</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {users.slice(0, 5).map((user, index) => {
            const rank = index + 1;
            const isTopThree = rank <= 3;
            
            return (
              <div 
                key={user.user_id} 
                className="flex items-center justify-between p-3 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div 
                    className={`h-10 w-10 rounded-full flex items-center justify-center text-sm font-bold ${
                      isTopThree 
                        ? 'bg-primary text-primary-foreground' 
                        : 'bg-muted text-muted-foreground'
                    }`}
                  >
                    #{rank}
                  </div>
                  <div>
                    <p className="text-sm font-medium">{user.username}</p>
                    <p className="text-xs text-muted-foreground">
                      {user.messages_count} messages · {user.dialogs_count} dialogs
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
