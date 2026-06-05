import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Send } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { createReview } from '@/services/reviews'
import type { Review } from '@/types/review'
import StarRating from '@/components/common/StarRating'
import Button from '@/components/ui/Button'
import toast from 'react-hot-toast'

interface Props {
  destinationId: number
  onSuccess: (review: Review) => void
}

export default function ReviewForm({ destinationId, onSuccess }: Props) {
  const { t } = useTranslation()
  const [rating, setRating] = useState(0)

  const schema = z.object({
    rating: z.number().min(1, t('review.selectRating')).max(5),
    comment: z.string().max(1000, t('review.maxChars')).optional(),
  })
  type FormData = z.infer<typeof schema>

  const { register, handleSubmit, setValue, reset, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { rating: 0, comment: '' },
  })

  const handleRatingChange = (v: number) => {
    setRating(v)
    setValue('rating', v, { shouldValidate: true })
  }

  const onSubmit = async (data: FormData) => {
    try {
      const review = await createReview(destinationId, { rating: data.rating, comment: data.comment || '' })
      onSuccess(review)
      reset()
      setRating(0)
      toast.success(t('review.submitted'))
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: Record<string, string[]> } }
      const msg = Object.values(axiosErr?.response?.data || {}).flat().join(' ') || t('review.failed')
      toast.error(msg)
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="bg-slate-50 dark:bg-slate-900/50 rounded-2xl p-5 space-y-4 border border-slate-100 dark:border-slate-700">
      <h3 className="font-semibold text-slate-900 dark:text-white">{t('review.writeTitle')}</h3>
      <div>
        <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">{t('review.yourRating')}</p>
        <StarRating value={rating} onChange={handleRatingChange} size="lg" />
        {errors.rating && <p className="mt-1 text-xs text-red-500">{errors.rating.message}</p>}
      </div>
      <div>
        <textarea
          {...register('comment')}
          placeholder={t('review.placeholder')}
          rows={3}
          className="input-base resize-none"
        />
        {errors.comment && <p className="mt-1 text-xs text-red-500">{errors.comment.message}</p>}
      </div>
      <Button type="submit" isLoading={isSubmitting} leftIcon={<Send className="w-4 h-4" />}>
        {t('review.submit')}
      </Button>
    </form>
  )
}
