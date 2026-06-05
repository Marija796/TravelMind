import Skeleton from '@/components/ui/Skeleton'

export default function DestinationSkeleton() {
  return (
    <div className="rounded-2xl overflow-hidden bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700/50 shadow-sm">
      <Skeleton className="w-full h-48" />
      <div className="p-4 space-y-2.5">
        <Skeleton variant="text" className="w-3/4 h-5" />
        <Skeleton variant="text" className="w-1/2 h-4" />
        <div className="flex gap-2 pt-1">
          <Skeleton className="w-16 h-5 rounded-full" />
          <Skeleton className="w-16 h-5 rounded-full" />
        </div>
        <div className="flex items-center justify-between pt-1">
          <Skeleton variant="text" className="w-20 h-4" />
          <Skeleton variant="text" className="w-16 h-4" />
        </div>
      </div>
    </div>
  )
}
