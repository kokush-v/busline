import { Text } from "@/components/ui/text";

type OrderItemProps = {
  id: string;
  date: string;
  status: string;
  total: string;
};

export function OrderItem({ id, date, status, total }: OrderItemProps) {
  return (
    <div className="border-border flex flex-col justify-between gap-2 rounded-lg border px-4 py-3 md:flex-row md:items-center">
      <div>
        <Text className="text-sm font-medium">Order - {id.slice(0, 8)}</Text>
        <Text role="date">{date}</Text>
      </div>
      <div className="flex items-center gap-3">
        <Text role="muted" className="text-xs">
          {status}
        </Text>
        <Text className="text-sm font-semibold">{total}</Text>
      </div>
    </div>
  );
}
