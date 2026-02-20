import { useState } from 'react';
import { useAppStore } from '../store/appStore';
import { supportTicketService } from '../api/services';

export default function Support() {
  const { language, setLoading, loading } = useAppStore();
  const [formData, setFormData] = useState({
    customer: 1,
    issue_type: 'other',
    description: '',
    priority: 'medium',
  });
  const [submitted, setSubmitted] = useState(false);
  const [ticketNumber, setTicketNumber] = useState('');

  const issueTypes = [
    { value: 'missing', label: language === 'ar' ? 'منتج مفقود' : 'Missing Item' },
    { value: 'damaged', label: language === 'ar' ? 'منتج تالف' : 'Damaged Item' },
    { value: 'wrong_item', label: language === 'ar' ? 'منتج خاطئ' : 'Wrong Item' },
    { value: 'delayed', label: language === 'ar' ? 'تأخير التسليم' : 'Delayed Delivery' },
    { value: 'quality', label: language === 'ar' ? 'مشكلة جودة' : 'Quality Issue' },
    { value: 'other', label: language === 'ar' ? 'أخرى' : 'Other' },
  ];

  const priorities = [
    { value: 'low', label: language === 'ar' ? 'منخفضة' : 'Low' },
    { value: 'medium', label: language === 'ar' ? 'متوسطة' : 'Medium' },
    { value: 'high', label: language === 'ar' ? 'عالية' : 'High' },
    { value: 'urgent', label: language === 'ar' ? 'عاجلة' : 'Urgent' },
  ];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      setLoading(true);
      const response = await supportTicketService.create(formData);
      setTicketNumber(response.data.ticket_number);
      setSubmitted(true);
      setFormData({
        customer: 1,
        issue_type: 'other',
        description: '',
        priority: 'medium',
      });
    } catch (error) {
      console.error('Error creating support ticket:', error);
      alert(language === 'ar' ? 'خطأ في إنشاء التذكرة' : 'Error creating support ticket');
    } finally {
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto bg-green-100 text-green-800 p-8 rounded-lg text-center">
          <p className="text-3xl font-bold mb-4">
            {language === 'ar' ? '✅ تم إنشاء التذكرة بنجاح!' : '✅ Support ticket created!'}
          </p>
          <p className="text-xl mb-4">
            {language === 'ar' ? 'رقم التذكرة:' : 'Ticket Number:'} <span className="font-mono font-bold">{ticketNumber}</span>
          </p>
          <p className="text-lg">
            {language === 'ar'
              ? 'سيتم التواصل معك قريباً'
              : 'We will contact you soon'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8 text-center">
        {language === 'ar' ? 'الدعم الفني' : 'Support'}
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Form */}
        <div className="lg:col-span-2">
          <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-8">
            <h2 className="text-2xl font-bold mb-6">
              {language === 'ar' ? 'فتح تذكرة دعم' : 'Create Support Ticket'}
            </h2>

            {/* Issue Type */}
            <div className="mb-6">
              <label className="block text-sm font-semibold mb-2">
                {language === 'ar' ? 'نوع المشكلة' : 'Issue Type'}
              </label>
              <select
                name="issue_type"
                value={formData.issue_type}
                onChange={handleChange}
                className="w-full px-4 py-2 border rounded focus:outline-none focus:border-blue-600"
              >
                {issueTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Priority */}
            <div className="mb-6">
              <label className="block text-sm font-semibold mb-2">
                {language === 'ar' ? 'الأولوية' : 'Priority'}
              </label>
              <select
                name="priority"
                value={formData.priority}
                onChange={handleChange}
                className="w-full px-4 py-2 border rounded focus:outline-none focus:border-blue-600"
              >
                {priorities.map((priority) => (
                  <option key={priority.value} value={priority.value}>
                    {priority.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Description */}
            <div className="mb-6">
              <label className="block text-sm font-semibold mb-2">
                {language === 'ar' ? 'وصف المشكلة' : 'Problem Description'}
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                required
                placeholder={
                  language === 'ar'
                    ? 'اشرح المشكلة بالتفصيل...'
                    : 'Describe the issue in detail...'
                }
                rows={6}
                className="w-full px-4 py-2 border rounded focus:outline-none focus:border-blue-600"
              />
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="w-full px-6 py-3 bg-blue-600 text-white rounded hover:bg-blue-700 transition font-bold disabled:bg-gray-400"
            >
              {loading
                ? language === 'ar'
                  ? 'جاري الإرسال...'
                  : 'Submitting...'
                : language === 'ar'
                ? 'فتح التذكرة'
                : 'Create Ticket'}
            </button>
          </form>
        </div>

        {/* Contact Info */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-md p-8 sticky top-20">
            <h2 className="text-2xl font-bold mb-6">
              {language === 'ar' ? 'معلومات التواصل' : 'Contact Info'}
            </h2>

            <div className="space-y-6">
              <div>
                <h3 className="font-bold mb-2">📧 {language === 'ar' ? 'البريد الإلكتروني' : 'Email'}</h3>
                <p className="text-gray-600">support@medistore.com</p>
              </div>

              <div>
                <h3 className="font-bold mb-2">📱 {language === 'ar' ? 'الهاتف' : 'Phone'}</h3>
                <p className="text-gray-600">+966 50 123 4567</p>
              </div>

              <div>
                <h3 className="font-bold mb-2">💬 {language === 'ar' ? 'WhatsApp' : 'WhatsApp'}</h3>
                <p className="text-gray-600">+966 50 123 4567</p>
              </div>

              <div>
                <h3 className="font-bold mb-2">🕐 {language === 'ar' ? 'ساعات العمل' : 'Working Hours'}</h3>
                <p className="text-gray-600">
                  {language === 'ar'
                    ? '24/7 متاح'
                    : '24/7 Available'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
