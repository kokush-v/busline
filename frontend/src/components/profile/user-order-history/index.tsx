"use client";

import { Suspense, useEffect, useMemo, useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { OrderList } from "./order-list";
import { OrderListSkeleton } from "./order-list-skeleton";
import { ProfileOrderFilterEnum } from "@/generated/api/model";

export function UserOrderHistory() {
  const [activeStatus, setActiveStatus] = useState<ProfileOrderFilterEnum>(
    ProfileOrderFilterEnum.ALL,
  );
  const [offset, setOffset] = useState(0);
  const limit = 10;

  useEffect(() => {
    setOffset(0);
  }, [activeStatus]);

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
          <div>
            <CardTitle>Order history</CardTitle>
            <CardDescription>Search and filter your orders</CardDescription>
          </div>
          <Tabs
            value={activeStatus}
            onValueChange={(value) =>
              setActiveStatus(value as ProfileOrderFilterEnum)
            }
          >
            <TabsList>
              {Object.values(ProfileOrderFilterEnum).map((tab) => (
                <TabsTrigger key={tab} value={tab}>
                  {tab}
                </TabsTrigger>
              ))}
            </TabsList>
          </Tabs>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <Separator />
        <Suspense
          key={`${activeStatus}-${offset}`}
          fallback={<OrderListSkeleton />}
        >
          <OrderList
            status={activeStatus}
            offset={offset}
            limit={limit}
            onOffsetChange={setOffset}
          />
        </Suspense>
      </CardContent>
    </Card>
  );
}
