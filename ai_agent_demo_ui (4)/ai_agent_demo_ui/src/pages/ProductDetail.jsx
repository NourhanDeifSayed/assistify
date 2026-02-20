import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useAppStore } from '../store/appStore';
import { productService } from '../api/services';

export default function ProductDetail() {
  const { id } = useParams();
  const { language, addToCart, setLoading, loading } = useAppStore();
  const [product, setProduct] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [quantity, setQuantity] = useState(1);

  useEffect(() => {
    fetchProduct();
    fetchRecommendations();
  }, [id]);

  const fetchProduct = async () => {
    try {
      setLoading(true);
      const response = await productService.getById(id);
      setProduct(response.data);
    } catch (error) {
      console.error('Error fetching product:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchRecommendations = async () => {
    try {
      const response = await productService.getRecommendations(id);
      setRecommendations(response.data);
    } catch (error) {
      console.error('Error fetching recommendations:', error);
    }
  };

  const handleAddToCart = () => {
    for (let i = 0; i < quantity; i++) {
      addToCart(product);
    }
    alert(language === 'ar' ? 'تمت إضافة المنتج للسلة' : 'Product added to cart');
  };

  if (loading) {
    return <div className="container mx-auto px-4 py-8 text-center">
      {language === 'ar' ? 'جاري التحميل...' : 'Loading...'}
    </div>;
  }

  if (!product) {
    return <div className="container mx-auto px-4 py-8 text-center">
      {language === 'ar' ? 'المنتج غير موجود' : 'Product not found'}
    </div>;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Product Details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
        {/* Image */}
        <div className="bg-gray-200 rounded-lg h-96 flex items-center justify-center">
          {product.image_url ? (
            <img src={product.image_url} alt={product.name} className="w-full h-full object-cover" />
          ) : (
            <span className="text-8xl">💊</span>
          )}
        </div>

        {/* Info */}
        <div>
          <h1 className="text-4xl font-bold mb-4">{product.name}</h1>
          <p className="text-gray-600 text-lg mb-6">{product.description}</p>

          {/* Price */}
          <div className="mb-6">
            {product.discount_price ? (
              <div className="flex gap-2 items-center mb-2">
                <span className="text-3xl font-bold text-green-600">{product.discount_price} ر.س</span>
                <span className="text-2xl text-gray-400 line-through">{product.price} ر.س</span>
              </div>
            ) : (
              <span className="text-3xl font-bold text-blue-600">{product.price} ر.س</span>
            )}
          </div>

          {/* Benefits */}
          {product.benefits && (
            <div className="mb-6">
              <h3 className="text-xl font-bold mb-2">{language === 'ar' ? 'الفوائد' : 'Benefits'}</h3>
              <p className="text-gray-700">{product.benefits}</p>
            </div>
          )}

          {/* Ingredients */}
          {product.ingredients && (
            <div className="mb-6">
              <h3 className="text-xl font-bold mb-2">{language === 'ar' ? 'المكونات' : 'Ingredients'}</h3>
              <p className="text-gray-700">{product.ingredients}</p>
            </div>
          )}

          {/* Dosage */}
          {product.dosage && (
            <div className="mb-6">
              <h3 className="text-xl font-bold mb-2">{language === 'ar' ? 'الجرعة' : 'Dosage'}</h3>
              <p className="text-gray-700">{product.dosage}</p>
            </div>
          )}

          {/* Stock */}
          <div className="mb-6">
            <p className="text-lg font-semibold">
              {language === 'ar' ? 'المخزون المتاح:' : 'Available Stock:'} {product.stock_quantity}
            </p>
          </div>

          {/* Quantity & Add to Cart */}
          <div className="flex gap-4 mb-6">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setQuantity(Math.max(1, quantity - 1))}
                className="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400"
              >
                -
              </button>
              <input
                type="number"
                value={quantity}
                onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
                className="w-12 text-center border rounded py-2"
              />
              <button
                onClick={() => setQuantity(quantity + 1)}
                className="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400"
              >
                +
              </button>
            </div>
            <button
              onClick={handleAddToCart}
              className="flex-1 px-6 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition font-bold"
            >
              {language === 'ar' ? 'أضف للسلة' : 'Add to Cart'}
            </button>
          </div>

          {/* Certifications */}
          {product.certifications && (
            <div className="bg-blue-50 p-4 rounded">
              <h3 className="font-bold mb-2">{language === 'ar' ? 'الشهادات' : 'Certifications'}</h3>
              <p className="text-sm text-gray-700">{JSON.stringify(product.certifications)}</p>
            </div>
          )}
        </div>
      </div>

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <div className="mt-12">
          <h2 className="text-3xl font-bold mb-8">
            {language === 'ar' ? 'منتجات ذات صلة' : 'Related Products'}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {recommendations.map((rec) => (
              <div key={rec.id} className="bg-white rounded-lg shadow-md overflow-hidden">
                <div className="bg-gray-200 h-40 flex items-center justify-center">
                  <span className="text-4xl">💊</span>
                </div>
                <div className="p-4">
                  <h3 className="font-bold mb-2">{rec.name}</h3>
                  <p className="text-green-600 font-bold">{rec.price} ر.س</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
