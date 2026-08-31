import React from 'react';
import { FileText, Download, TrendingUp, Search } from 'lucide-react';

export const FinalReport: React.FC = () => {
  return (
    <div className="w-full max-w-5xl mx-auto pb-12 animate-in fade-in slide-in-from-bottom-4 duration-500">
      
      {/* Header */}
      <div className="mb-8 border-b border-outline-variant/30 pb-6 flex justify-between items-end">
        <div>
          <h1 className="font-headline-lg text-headline-lg text-primary font-bold">
            Wishlist to Purchase Analysis
          </h1>
        </div>
        <button 
          className="flex items-center gap-2 bg-surface-container border border-outline-variant/50 hover:bg-surface-container-high transition-colors px-4 py-2 rounded-md shadow-sm font-label-md text-label-md text-on-surface"
          onClick={() => alert("Downloading relevant_reviews.csv...")}
        >
          <Download size={16} />
          Download Dataset
        </button>
      </div>


      {/* Section 4: Purchase-Barrier Frequency */}
      <section className="mb-10">
        <h2 className="font-headline-sm text-headline-sm text-on-background mb-4 flex items-center gap-2">
          <TrendingUp className="text-secondary" size={20} />
          <span className="font-bold">Purchase-Barrier Frequency</span>
        </h2>
        <div className="glass-panel rounded-lg overflow-hidden">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-surface-container text-on-surface-variant font-label-md">
                <th className="px-4 py-3 border-b border-outline-variant/30">Purchase Barrier</th>
                <th className="px-4 py-3 border-b border-outline-variant/30">Mentions</th>
                <th className="px-4 py-3 border-b border-outline-variant/30">Impact Volume</th>
              </tr>
            </thead>
            <tbody className="font-body-sm text-on-surface">
              <tr className="hover:bg-surface-container/50">
                <td className="px-4 py-3 border-b border-outline-variant/10 font-bold">Reviews/Ratings</td>
                <td className="px-4 py-3 border-b border-outline-variant/10">726</td>
                <td className="px-4 py-3 border-b border-outline-variant/10 text-error font-bold">75.86%</td>
              </tr>
              <tr className="hover:bg-surface-container/50">
                <td className="px-4 py-3 border-b border-outline-variant/10 font-bold">Availability</td>
                <td className="px-4 py-3 border-b border-outline-variant/10">707</td>
                <td className="px-4 py-3 border-b border-outline-variant/10 text-error font-bold">73.88%</td>
              </tr>
              <tr className="hover:bg-surface-container/50">
                <td className="px-4 py-3 border-b border-outline-variant/10 font-bold">Price</td>
                <td className="px-4 py-3 border-b border-outline-variant/10">662</td>
                <td className="px-4 py-3 border-b border-outline-variant/10 text-error font-bold">69.17%</td>
              </tr>
              <tr className="hover:bg-surface-container/50">
                <td className="px-4 py-3 border-b border-outline-variant/10">Size/Fit</td>
                <td className="px-4 py-3 border-b border-outline-variant/10">525</td>
                <td className="px-4 py-3 border-b border-outline-variant/10 text-yellow-600">54.86%</td>
              </tr>
              <tr className="hover:bg-surface-container/50">
                <td className="px-4 py-3 border-b border-outline-variant/10">Trust</td>
                <td className="px-4 py-3 border-b border-outline-variant/10">410</td>
                <td className="px-4 py-3 border-b border-outline-variant/10 text-yellow-600">42.84%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      {/* Sections 6 & 8: Hypothesis Prioritization */}
      <section className="mb-10">
        <h2 className="font-headline-sm text-headline-sm text-on-background mb-4 flex items-center gap-2">
          <Search className="text-tertiary" size={20} />
          <span className="font-bold">Hypothesis Prioritization</span>
        </h2>
        <div className="glass-panel rounded-lg overflow-hidden border border-tertiary/20 shadow-sm">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-tertiary-container/30 text-on-surface-variant font-label-md">
                <th className="px-4 py-4 border-b border-outline-variant/30">Hypothesis</th>
                <th className="px-4 py-4 border-b border-outline-variant/30 text-center">Evidence Vol.</th>
                <th className="px-4 py-4 border-b border-outline-variant/30 text-center">User Impact</th>
                <th className="px-4 py-4 border-b border-outline-variant/30 text-center">Confidence</th>
                <th className="px-4 py-4 border-b border-outline-variant/30 text-center">Priority</th>
              </tr>
            </thead>
            <tbody className="font-body-sm text-on-surface">
              
              {/* H1 */}
              <tr className="hover:bg-surface-container/50">
                <td className="px-4 py-4 border-b border-outline-variant/10">
                  <span className="font-bold block mb-1">H1: Delivery Trust Issues (54.9%)</span>
                  <span className="text-on-surface-variant text-xs line-clamp-2">Users keep items in their wishlist because they are afraid Myntra will suddenly cancel their order or delay the delivery for weeks.</span>
                </td>
                <td className="px-4 py-4 border-b border-outline-variant/10 text-center">
                  <span className="bg-error-container text-on-error-container px-2 py-1 rounded font-bold text-xs uppercase">High</span>
                </td>
                <td className="px-4 py-4 border-b border-outline-variant/10 text-center">
                  <span className="bg-error-container text-on-error-container px-2 py-1 rounded font-bold text-xs uppercase">High</span>
                </td>
                <td className="px-4 py-4 border-b border-outline-variant/10 text-center">
                  <span className="bg-error-container text-on-error-container px-2 py-1 rounded font-bold text-xs uppercase">High</span>
                </td>
                <td className="px-4 py-4 border-b border-outline-variant/10 text-center">
                  <span className="bg-primary text-white px-3 py-1.5 rounded-md font-bold text-xs uppercase shadow-sm">P1</span>
                </td>
              </tr>

              {/* H2 */}
              <tr className="hover:bg-surface-container/50">
                <td className="px-4 py-4 border-b border-outline-variant/10">
                  <span className="font-bold block mb-1">H2: Fear of Bad Returns & Support (71.4%)</span>
                  <span className="text-on-surface-variant text-xs line-clamp-2">Users hesitate to buy because they worry the clothes will look cheap in real life, and they know getting a refund from the AI bot is incredibly frustrating.</span>
                </td>
                <td className="px-4 py-4 border-b border-outline-variant/10 text-center">
                  <span className="bg-secondary-container text-on-secondary-container px-2 py-1 rounded font-bold text-xs uppercase">Medium</span>
                </td>
                <td className="px-4 py-4 border-b border-outline-variant/10 text-center">
                  <span className="bg-error-container text-on-error-container px-2 py-1 rounded font-bold text-xs uppercase">High</span>
                </td>
                <td className="px-4 py-4 border-b border-outline-variant/10 text-center">
                  <span className="bg-secondary-container text-on-secondary-container px-2 py-1 rounded font-bold text-xs uppercase">Medium</span>
                </td>
                <td className="px-4 py-4 border-b border-outline-variant/10 text-center">
                  <span className="bg-secondary text-white px-3 py-1.5 rounded-md font-bold text-xs uppercase shadow-sm">P2</span>
                </td>
              </tr>

              {/* H3 */}
              <tr className="hover:bg-surface-container/50">
                <td className="px-4 py-4 border-b border-outline-variant/10">
                  <span className="font-bold block mb-1">H3: Hidden Fees & Waiting for Sales (69.1%)</span>
                  <span className="text-on-surface-variant text-xs line-clamp-2">Users abandon their carts because they are waiting for massive sales to drop, or they get angry when a non-refundable "platform fee" is suddenly added at the very end of checkout.</span>
                </td>
                <td className="px-4 py-4 border-b border-outline-variant/10 text-center">
                  <span className="bg-surface-container-highest text-on-surface-variant px-2 py-1 rounded font-bold text-xs uppercase">Low</span>
                </td>
                <td className="px-4 py-4 border-b border-outline-variant/10 text-center">
                  <span className="bg-error-container text-on-error-container px-2 py-1 rounded font-bold text-xs uppercase">High</span>
                </td>
                <td className="px-4 py-4 border-b border-outline-variant/10 text-center">
                  <span className="bg-surface-container-highest text-on-surface-variant px-2 py-1 rounded font-bold text-xs uppercase">Low</span>
                </td>
                <td className="px-4 py-4 border-b border-outline-variant/10 text-center">
                  <span className="bg-tertiary text-white px-3 py-1.5 rounded-md font-bold text-xs uppercase shadow-sm">P3</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      {/* Legend / Explanation Section */}
      <section className="mb-10 animate-in fade-in slide-in-from-bottom-6 duration-700">
        <div className="bg-surface-container-low border-l-4 border-primary p-6 rounded-r-lg shadow-sm">
          <h3 className="font-headline-sm text-headline-sm text-on-surface mb-3 flex items-center gap-2">
            <span className="material-symbols-outlined text-primary">info</span>
            Understanding the Barrier Metrics
          </h3>
          <p className="font-body-md text-on-surface-variant mb-4">
            The percentages in the hypotheses above represent the frequency of specific complaints found in the analyzed dataset. Here is what they mean in context:
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-4">
            <div>
              <h4 className="font-bold text-on-surface flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-error"></span> Price (69.1%)</h4>
              <p className="font-body-sm text-on-surface-variant ml-3.5">Users abandoning purchases because of high base costs, sudden non-refundable platform fees added at checkout, or finding cheaper alternatives on competitor platforms.</p>
            </div>
            <div>
              <h4 className="font-bold text-on-surface flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-primary"></span> Trust (42.8%) & Delivery (54.9%)</h4>
              <p className="font-body-sm text-on-surface-variant ml-3.5">Users hesitating to buy because they fear Myntra will suddenly cancel their order or delay delivery by weeks based on past negative experiences.</p>
            </div>
            <div>
              <h4 className="font-bold text-on-surface flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-secondary"></span> Appearance (71.4%)</h4>
              <p className="font-body-sm text-on-surface-variant ml-3.5">Users keeping items in the wishlist because they don't trust the studio photos and fear the real product's color or material will look completely different.</p>
            </div>
            <div>
              <h4 className="font-bold text-on-surface flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-tertiary"></span> Quality (22.4%) & Returns</h4>
              <p className="font-body-sm text-on-surface-variant ml-3.5">Anxiety over receiving a defective or used item, compounded by the fear of getting stuck in an automated "AI-only" customer support loop when trying to get a refund.</p>
            </div>
          </div>
        </div>
      </section>

    </div>
  );
};
