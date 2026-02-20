import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAppStore } from '../store/appStore';
import { productService } from '../api/services';

export default function Products() {
  const { language, products, setProducts, addToCart, setLoading, loading } = useAppStore();
  const [filters, setFilters] = useState({ status: 'active' });

  useEffect(() => {
    fetchProducts();
  }, [filters]);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const response = await productService.getActive();
      setProducts(response.data);
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = (product) => {
    addToCart(product);
    alert(language === 'ar' ? 'تمت إضافة المنتج للسلة' : 'Product added to cart');
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8">
        {language === 'ar' ? 'المنتجات' : 'Products'}
      </h1>

      {loading ? (
        <div className="text-center py-12">
          <p>{language === 'ar' ? 'جاري التحميل...' : 'Loading...'}</p>
        </div>
      ) : products.length === 0 ? (
        <div className="text-center py-12">
          <p>{language === 'ar' ? 'لا توجد منتجات' : 'No products found'}</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {products.map((product) => (
            <div key={product.id} className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition">
              {/* Product Image */}
              <div className="bg-gray-200 h-48 flex items-center justify-center">
                {product.image_url ? (
                  <img src={product.image_url} alt={product.name} className="w-full h-full object-cover" />
                ) : (
                  <span className="text-4xl">💊</span>
                )}
              </div>

              {/* Product Info */}
              <div className="p-6">
                <h3 className="text-xl font-bold mb-2">{product.name}</h3>
                <p className="text-gray-600 text-sm mb-4">{product.description}</p>

                {/* Benefits */}
                {product.benefits && (
                  <div className="mb-4">
                    <p className="text-sm font-semibold text-gray-700 mb-1">
                      {language === 'ar' ? 'الفوائد:' : 'Benefits:'}
                    </p>
                    <p className="text-sm text-gray-600">{product.benefits}</p>
                  </div>
                )}

                {/* Price */}
                <div className="mb-4">
                  {product.discount_price ? (
                    <div className="flex gap-2 items-center">
                      <span className="text-2xl font-bold text-green-600">{product.discount_price} ر.س</span>
                      <span className="text-lg text-gray-400 line-through">{product.price} ر.س</span>
                    </div>
                  ) : (
                    <span className="text-2xl font-bold text-blue-600">{product.price} ر.س</span>
                  )}
                </div>

                {/* Stock */}
                <div className="mb-4">
                  <p className="text-sm text-gray-600">
                    {language === 'ar' ? 'المخزون:' : 'Stock:'} {product.stock_quantity}
                  </p>
                </div>

                {/* Buttons */}
                <div className="flex gap-2">
                  <Link
                    to={`/products/${product.id}`}
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition text-center"
                  >
                    {language === 'ar' ? 'التفاصيل' : 'Details'}
                  </Link>
                  <button
                    onClick={() => handleAddToCart(product)}
                    className="flex-1 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition"
                  >
                    {language === 'ar' ? 'أضف للسلة' : 'Add to Cart'}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
