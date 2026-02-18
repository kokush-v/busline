"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { XIcon } from "lucide-react";
import { Text } from "@/components/ui/text";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { FormField } from "@/components/ui/form-field";
import { UserRoleGroups } from "@/generated/api/model/userRoleGroups";
import {
  userCreateSchema,
  userUpdateSchema,
  type UserCreateFormValues,
  type UserUpdateFormValues,
} from "./schema";
import type { UserFormPanelProps } from "./types";

export function UserFormPanel({
  editingUser,
  onClose,
  onSubmit,
  isMutating,
}: UserFormPanelProps) {
  const isEditing = !!editingUser;

  if (isEditing) {
    return (
      <EditUserForm
        editingUser={editingUser}
        onClose={onClose}
        onSubmit={onSubmit}
        isMutating={isMutating}
      />
    );
  }

  return (
    <CreateUserForm
      onClose={onClose}
      onSubmit={onSubmit}
      isMutating={isMutating}
    />
  );
}

function CreateUserForm({
  onClose,
  onSubmit,
  isMutating,
}: Omit<UserFormPanelProps, "editingUser">) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<UserCreateFormValues>({
    resolver: zodResolver(userCreateSchema),
    defaultValues: {
      email: "",
      name: "",
      phone_number: "",
      role: UserRoleGroups.USER,
    },
  });

  return (
    <div className="-my-8 -mr-3 flex w-96 shrink-0 flex-col border-l px-6 py-6 sm:-mr-4">
      <div className="mb-4 flex items-center justify-between">
        <Text role="h4">Add User</Text>
        <Button variant="ghost" size="icon-sm" onClick={onClose}>
          <XIcon className="size-4" />
        </Button>
      </div>

      <form
        onSubmit={handleSubmit(onSubmit)}
        className="flex flex-1 flex-col gap-4"
      >
        <FormField id="user-email" label="Email" error={errors.email?.message}>
          <Input
            id="user-email"
            type="email"
            placeholder="user@example.com"
            {...register("email")}
          />
        </FormField>

        <FormField id="user-name" label="Name" error={errors.name?.message}>
          <Input id="user-name" placeholder="John Doe" {...register("name")} />
        </FormField>

        <FormField
          id="user-phone"
          label="Phone"
          error={errors.phone_number?.message}
        >
          <Input
            id="user-phone"
            placeholder="+380..."
            {...register("phone_number")}
          />
        </FormField>

        <FormField id="user-role" label="Role" error={errors.role?.message}>
          <select
            id="user-role"
            className="border-input bg-background ring-offset-background placeholder:text-muted-foreground focus-visible:ring-ring flex h-9 w-full rounded-md border px-3 py-1 text-sm shadow-sm focus-visible:ring-1 focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50"
            {...register("role")}
          >
            <option value={UserRoleGroups.USER}>USER</option>
            <option value={UserRoleGroups.ADMIN}>ADMIN</option>
          </select>
        </FormField>

        <div className="mt-auto flex gap-2 pt-4">
          <Button
            type="button"
            variant="outline"
            className="flex-1"
            onClick={onClose}
          >
            Cancel
          </Button>
          <Button type="submit" className="flex-1" disabled={isMutating}>
            Create
          </Button>
        </div>
      </form>
    </div>
  );
}

function EditUserForm({
  editingUser,
  onClose,
  onSubmit,
  isMutating,
}: UserFormPanelProps & {
  editingUser: NonNullable<UserFormPanelProps["editingUser"]>;
}) {
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<UserUpdateFormValues>({
    resolver: zodResolver(userUpdateSchema),
    defaultValues: {
      name: editingUser.name ?? "",
      phone_number: editingUser.phone_number ?? "",
      role: editingUser.role,
      is_active: editingUser.is_active,
    },
  });

  const isActive = watch("is_active");

  return (
    <div className="-my-8 -mr-3 flex w-96 shrink-0 flex-col border-l px-6 py-6 sm:-mr-4">
      <div className="mb-4 flex items-center justify-between">
        <Text role="h4">Edit User</Text>
        <Button variant="ghost" size="icon-sm" onClick={onClose}>
          <XIcon className="size-4" />
        </Button>
      </div>

      <form
        onSubmit={handleSubmit(onSubmit)}
        className="flex flex-1 flex-col gap-4"
      >
        <div className="space-y-2">
          <Label>Email</Label>
          <Input value={editingUser.email} disabled />
        </div>

        <FormField id="user-name" label="Name" error={errors.name?.message}>
          <Input id="user-name" placeholder="John Doe" {...register("name")} />
        </FormField>

        <FormField
          id="user-phone"
          label="Phone"
          error={errors.phone_number?.message}
        >
          <Input
            id="user-phone"
            placeholder="+380..."
            {...register("phone_number")}
          />
        </FormField>

        <FormField id="user-role" label="Role" error={errors.role?.message}>
          <select
            id="user-role"
            className="border-input bg-background ring-offset-background placeholder:text-muted-foreground focus-visible:ring-ring flex h-9 w-full rounded-md border px-3 py-1 text-sm shadow-sm focus-visible:ring-1 focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50"
            {...register("role")}
          >
            <option value={UserRoleGroups.USER}>USER</option>
            <option value={UserRoleGroups.ADMIN}>ADMIN</option>
          </select>
        </FormField>

        <div className="flex items-center gap-2">
          <Checkbox
            id="user-active"
            checked={isActive}
            onCheckedChange={(checked) =>
              setValue("is_active", checked === true)
            }
          />
          <Label htmlFor="user-active">Active</Label>
        </div>

        <div className="mt-auto flex gap-2 pt-4">
          <Button
            type="button"
            variant="outline"
            className="flex-1"
            onClick={onClose}
          >
            Cancel
          </Button>
          <Button type="submit" className="flex-1" disabled={isMutating}>
            Save
          </Button>
        </div>
      </form>
    </div>
  );
}
