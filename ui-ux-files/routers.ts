import { COOKIE_NAME } from "@shared/const";
import { getSessionCookieOptions } from "./_core/cookies";
import { systemRouter } from "./_core/systemRouter";
import { publicProcedure, router, protectedProcedure } from "./_core/trpc";
import { invokeLLM } from "./_core/llm";
import { searchProducts, getProductById, getRelatedProducts, formatProductInfo, formatTrackingInfo, getAllProductsContext, mockOrders } from "./chatData";

export const appRouter = router({
  system: systemRouter,

  auth: router({
    me: publicProcedure.query(opts => opts.ctx.user),
    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);
      ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      return {
        success: true,
      } as const;
    }),
  }),

  dashboard: router({
    stats: protectedProcedure.query(async ({ ctx }) => {
      return {
        conversion: { conversionRate: 0, avgOrderValue: 0, repeatCustomerRate: 0 },
        shipments: { totalShipments: 0, delayedShipments: 0, deliveredShipments: 0 },
        orders: { totalOrders: 0, pendingOrders: 0, deliveredOrders: 0 },
        tickets: { openTickets: 0, resolvedTickets: 0, avgResolutionTime: 0 },
      };
    }),
  }),

  orders: router({
    list: protectedProcedure.query(async ({ ctx }) => {
      return [];
    }),
    getById: protectedProcedure.input((val) => {
      if (typeof val === "number") return val;
      throw new Error("Expected number");
    }).query(async ({ input }) => {
      return null;
    }),
  }),

  tickets: router({
    list: protectedProcedure.query(async ({ ctx }) => {
      return [];
    }),
    create: protectedProcedure.input((val) => {
      if (typeof val === "object" && val !== null) return val;
      throw new Error("Expected object");
    }).mutation(async ({ input, ctx }) => {
      return { success: true, id: 1 };
    }),
  }),

  analytics: router({
    conversionFunnel: protectedProcedure.query(async ({ ctx }) => {
      return {
        preSale: 100,
        orderPlacement: 75,
        shipping: 70,
        postSale: 65,
      };
    }),
    customerBehavior: protectedProcedure.query(async ({ ctx }) => {
      return {
        highSpenders: 0,
        offerAcceptanceRate: 0,
        retentionRate: 0,
      };
    }),
  }),

  chat: router({
    sendMessage: publicProcedure
      .input((val) => {
        if (typeof val === "object" && val !== null && "message" in val) return val as { message: string };
        throw new Error("Expected object with message property");
      })
      .mutation(async ({ input }) => {
        try {
          const userMessage = input.message.toLowerCase();
          
          // Search for relevant products
          const searchResults = searchProducts(input.message);
          let productContext = "";
          
          if (searchResults.length > 0) {
            productContext = "\n\nRelevant products found:\n";
            searchResults.forEach((product) => {
              productContext += `\n${formatProductInfo(product)}`;
              
              const related = getRelatedProducts(product.id);
              if (related.length > 0) {
                productContext += "\n\nRelated products:";
                related.forEach((relProd) => {
                  productContext += `\n- ${relProd.name} (${relProd.price} ${relProd.currency}): ${relProd.description}`;
                });
              }
            });
          }
          
          // Check for tracking queries
          const isTrackingQuery = userMessage.includes("track") || 
                                 userMessage.includes("order") ||
                                 userMessage.includes("delivery") ||
                                 userMessage.includes("shipping");
          
          let trackingContext = "";
          if (isTrackingQuery && mockOrders.length > 0) {
            trackingContext = "\n\nOrder Tracking Information:\n";
            mockOrders.forEach((order) => {
              trackingContext += `\n${formatTrackingInfo(order)}`;
            });
          }
          
          const systemPrompt = `You are MediCare AI, a helpful and knowledgeable assistant for a medical devices e-commerce platform.

Our Products:
${getAllProductsContext()}

Your Key Responsibilities:
1. Help customers find the right medical devices for their needs
2. Provide detailed product information including benefits and features
3. Suggest related products that complement their interests
4. Help with order placement and provide order confirmation details
5. Provide tracking information for existing orders
6. Answer questions about delivery, payment methods, and returns
7. Be friendly, professional, and helpful
8. Respond in Arabic if the user writes in Arabic, otherwise respond in English

Important Guidelines:
- When a customer is interested in a product, offer to help them add it to their cart or place an order
- When asked about orders or tracking, provide detailed status updates
- Always be honest about product features and benefits
- Suggest complementary products when appropriate
- Provide helpful tips for using medical devices safely
${productContext}${trackingContext}`;

          const response = await invokeLLM({
            messages: [
              {
                role: "system",
                content: systemPrompt,
              },
              {
                role: "user",
                content: input.message,
              },
            ],
          });

          const content = response.choices?.[0]?.message?.content;
          if (typeof content === "string") {
            return content;
          }
          return "I could not process your request. Please try again.";
        } catch (error) {
          console.error("LLM Error:", error);
          return "Sorry, I encountered an error processing your request. Please try again later.";
        }
      }),
  }),
});

export type AppRouter = typeof appRouter;
