import { PlusIcon } from "lucide-react";
import { Text } from "@/components/ui/text";
import { Button } from "@/components/ui/button";

type UsersHeaderProps = {
  onAddUser: () => void;
};

export function UsersHeader({ onAddUser }: UsersHeaderProps) {
  return (
    <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
      <div>
        <Text role="h2">Users</Text>
        <Text role="muted">Manage users and their roles.</Text>
      </div>
      <Button onClick={onAddUser}>
        <PlusIcon className="size-4" />
        Add User
      </Button>
    </div>
  );
}
