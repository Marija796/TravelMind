import Skeleton from '@/components/ui/Skeleton'

export default function SimilarUserSkeleton() {
  return (
    <div className="rounded-2xl overflow-hidden bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700/50 shadow-sm p-5 flex flex-col items-center gap-3">
      <Skeleton variant="circular" className="w-16 h-16" />
      <Skeleton variant="text" className="w-2/3 h-4" />
      <Skeleton variant="text" className="w-1/3 h-3" />
      <Skeleton variant="text" className="w-full h-3" />
    </div>
  )
}
