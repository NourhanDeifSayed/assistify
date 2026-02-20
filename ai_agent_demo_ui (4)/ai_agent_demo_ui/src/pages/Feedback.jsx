import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/appStore';
import { feedbackService } from '../api/services';

export default function Feedback() {
  const { orderId } = useParams();
  const navigate = useNavigate();
  const { language, setLoading, loading } = useAppStore();
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (rating === 0) {
      alert(language === 'ar' ? 'يرجى اختيار تقييم' : 'Please select a rating');
      return;
    }

    try {
      setLoading(true);
      await feedbackService.create({
        order: orderId,
        customer: 1, // Placeholder
        rating,
        comment,
      });
      setSubmitted(true);
      setTimeout(() => navigate('/'), 2000);
    } catch (error) {
      console.error('Error submitting feedback:', error);
      alert(language === 'ar' ? 'خطأ في إرسال التقييم' : 'Error submitting feedback');
    } finally {
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <div className="bg-green-100 text-green-800 p-8 rounded-lg max-w-md mx-auto">
          <p className="text-2xl font-bold mb-4">
            {language === 'ar' ? '✅ شكراً لتقييمك!' : '✅ Thank you for your feedback!'}
          </p>
          <p>
            {language === 'ar'
              ? 'سيتم إعادة توجيهك للصفحة الرئيسية...'
              : 'Redirecting to home page...'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8 text-center">
        {language === 'ar' ? 'قيّم طلبك' : 'Rate Your Order'}
      </h1>

      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-8">
        <form onSubmit={handleSubmit}>
          {/* Rating */}
          <div className="mb-8">
            <label className="block text-xl font-bold mb-4">
              {language === 'ar' ? 'كيف تقيّم خدمتنا؟' : 'How would you rate our service?'}
            </label>
            <div className="flex gap-4 justify-center">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  type="button"
                  onClick={() => setRating(star)}
                  className={`text-5xl transition transform hover:scale-110 ${
                    star <= rating ? 'text-yellow-400' : 'text-gray-300'
                  }`}
                >
                  ⭐
                </button>
              ))}
            </div>
            {rating > 0 && (
              <p className="text-center mt-4 text-lg font-semibold">
                {language === 'ar'
                  ? {
                      1: 'سيء جداً',
                      2: 'سيء',
                      3: 'عادي',
                      4: 'جيد',
                      5: 'ممتاز',
                    }[rating]
                  : {
                      1: 'Very Bad',
                      2: 'Bad',
                      3: 'Average',
                      4: 'Good',
                      5: 'Excellent',
                    }[rating]}
              </p>
            )}
          </div>

          {/* Comment */}
          <div className="mb-8">
            <label className="block text-lg font-bold mb-4">
              {language === 'ar' ? 'تعليقك (اختياري)' : 'Your Comment (Optional)'}
            </label>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder={
                language === 'ar'
                  ? 'شارك تجربتك معنا...'
                  : 'Share your experience with us...'
              }
              rows={6}
              className="w-full px-4 py-2 border rounded focus:outline-none focus:border-blue-600"
            />
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading || rating === 0}
            className="w-full px-6 py-3 bg-blue-600 text-white rounded hover:bg-blue-700 transition font-bold disabled:bg-gray-400"
          >
            {loading
              ? language === 'ar'
                ? 'جاري الإرسال...'
                : 'Submitting...'
              : language === 'ar'
              ? 'إرسال التقييم'
              : 'Submit Rating'}
          </button>
        </form>
      </div>
    </div>
  );
}
