"use client";

import { useState, useMemo, useCallback } from "react";
import { useGetUsers } from "@/generated/api/endpoints/users/users";
import type { UserRead } from "@/generated/api/model";
import { UserSortBy } from "@/generated/api/model/userSortBy";
import { SortOrder } from "@/generated/api/model/sortOrder";
import { useUsersApi } from "@/hooks/use-users-api";
import type {
  UserCreateFormValues,
  UserUpdateFormValues,
} from "@/components/forms/user/schema";
import {
  UsersHeader,
  UserSearchInput,
  UsersTable,
  UserFormPanel,
  DeleteUserDialog,
} from "@/components/users";
import { AdminPageLayout } from "@/components/admin/admin-page-layout";

const PAGE_SIZE = 20;

export default function UsersPage() {
  const [search, setSearch] = useState("");
  const [offset, setOffset] = useState(0);
  const [sortBy, setSortBy] = useState<UserSortBy>(UserSortBy.email);
  const [sortOrder, setSortOrder] = useState<SortOrder>(SortOrder.asc);
  const [deleteTarget, setDeleteTarget] = useState<UserRead | null>(null);
  const [editingUserId, setEditingUserId] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);

  const handleSearchChange = useCallback((value: string) => {
    setSearch(value);
    setOffset(0);
  }, []);

  const panelOpen = isCreating || !!editingUserId;

  const { data, isLoading, isError, refetch } = useGetUsers({
    search: search || undefined,
    limit: PAGE_SIZE,
    offset,
    sort_by: sortBy,
    sort_order: sortOrder,
  });

  const { createUser, updateUser, deleteUser, isMutating } = useUsersApi();

  const users = useMemo(() => data?.items ?? [], [data?.items]);
  const total = data?.total ?? 0;

  const handleSortChange = (field: UserSortBy) => {
    if (field === sortBy) {
      setSortOrder((prev) =>
        prev === SortOrder.asc ? SortOrder.desc : SortOrder.asc,
      );
    } else {
      setSortBy(field);
      setSortOrder(SortOrder.asc);
    }
    setOffset(0);
  };

  const handleOffsetChange = (newOffset: number) => {
    setOffset(newOffset);
  };

  const editingUser = useMemo(
    () => users.find((u) => u.id === editingUserId) ?? null,
    [users, editingUserId],
  );

  const openCreatePanel = () => {
    setEditingUserId(null);
    setIsCreating(true);
  };

  const openEditPanel = (user: UserRead) => {
    setIsCreating(false);
    setEditingUserId(user.id);
  };

  const closePanel = () => {
    setEditingUserId(null);
    setIsCreating(false);
  };

  const handleFormSubmit = (
    payload: UserCreateFormValues | UserUpdateFormValues,
  ) => {
    if (editingUser) {
      updateUser(editingUser.id, payload as UserUpdateFormValues);
    } else {
      createUser(payload as UserCreateFormValues, closePanel);
    }
  };

  const handleDelete = () => {
    if (!deleteTarget) return;
    deleteUser(deleteTarget.id, () => {
      if (editingUserId === deleteTarget.id) closePanel();
      setDeleteTarget(null);
    });
  };

  return (
    <AdminPageLayout
      panel={
        panelOpen && (
          <UserFormPanel
            key={editingUserId ?? "new"}
            editingUser={editingUser}
            onClose={closePanel}
            onSubmit={handleFormSubmit}
            isMutating={isMutating}
          />
        )
      }
    >
      <UsersHeader onAddUser={openCreatePanel} />
      <UserSearchInput value={search} onChange={handleSearchChange} />
      <UsersTable
        users={users}
        isLoading={isLoading}
        isError={isError}
        onRetry={refetch}
        search={search}
        editingUserId={editingUserId ?? undefined}
        onEdit={openEditPanel}
        onDelete={setDeleteTarget}
        sortBy={sortBy}
        sortOrder={sortOrder}
        onSortChange={handleSortChange}
        offset={offset}
        limit={PAGE_SIZE}
        total={total}
        onOffsetChange={handleOffsetChange}
      />

      <DeleteUserDialog
        user={deleteTarget}
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
        disabled={isMutating}
      />
    </AdminPageLayout>
  );
}
