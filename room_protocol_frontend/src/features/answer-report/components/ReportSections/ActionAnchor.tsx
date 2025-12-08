import React from 'react';
import { Anchor, Zap, Quote } from 'lucide-react';
import { ActionAnchor } from '../../types/report';

interface ActionAnchorSectionProps {
  data: ActionAnchor;
}

export default function ActionAnchorSection({ data }: ActionAnchorSectionProps) {
  return (
    <div className="space-y-8">
      {/* Title */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Part 5: Action Anchor Forging</h2>
        <p className="text-gray-600">Condensing the wisdom of the entire report into a personal proverb as a long-term action guide</p>
      </div>

      {/* Core Verb */}
      <div className="bg-indigo-50 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <Zap className="w-6 h-6 text-indigo-600 mr-3" />
          <h3 className="text-xl font-semibold text-gray-900">Core Verb</h3>
        </div>
        <div className="bg-white rounded-lg p-6 border-l-4 border-indigo-500">
          <div className="text-center">
            <div className="w-20 h-20 bg-indigo-100 rounded-full mx-auto mb-4 flex items-center justify-center">
              <span className="text-2xl font-bold text-indigo-600">{data.core_verb}</span>
            </div>
            <p className="text-gray-600">The action word that best represents the essence of the strategy</p>
          </div>
        </div>
      </div>

      {/* Action Proverb */}
      <div className="bg-gradient-to-br from-purple-50 via-pink-50 to-orange-50 rounded-lg p-8">
        <div className="flex items-center justify-center mb-6">
          <Anchor className="w-8 h-8 text-purple-600 mr-3" />
          <h3 className="text-2xl font-semibold text-gray-900">Action Proverb</h3>
        </div>

        <div className="bg-white rounded-lg p-8 border-2 border-purple-200 shadow-lg">
          <div className="text-center">
            <Quote className="w-12 h-12 text-purple-400 mx-auto mb-4" />
            <blockquote className="text-3xl font-bold text-gray-900 mb-4 leading-relaxed">
              {data.proverb}
            </blockquote>
            <div className="w-24 h-1 bg-gradient-to-r from-purple-400 to-pink-400 mx-auto mb-4"></div>
            <p className="text-gray-600 italic">
              Your Personal Action Guide
            </p>
          </div>
        </div>
      </div>

      {/* Usage Guide */}
      <div className="bg-yellow-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 text-center">How to Use This Proverb</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg p-4 text-center">
            <div className="w-12 h-12 bg-yellow-100 rounded-full mx-auto mb-3 flex items-center justify-center">
              <span className="text-yellow-600 font-bold">1</span>
            </div>
            <h4 className="font-semibold text-gray-900 mb-2">Daily Reminder</h4>
            <p className="text-sm text-gray-600">Set this as your phone wallpaper or sticky note to remind yourself daily</p>
          </div>

          <div className="bg-white rounded-lg p-4 text-center">
            <div className="w-12 h-12 bg-yellow-100 rounded-full mx-auto mb-3 flex items-center justify-center">
              <span className="text-yellow-600 font-bold">2</span>
            </div>
            <h4 className="font-semibold text-gray-900 mb-2">Decision Guide</h4>
            <p className="text-sm text-gray-600">When facing choices, ask yourself if it aligns with this principle</p>
          </div>

          <div className="bg-white rounded-lg p-4 text-center">
            <div className="w-12 h-12 bg-yellow-100 rounded-full mx-auto mb-3 flex items-center justify-center">
              <span className="text-yellow-600 font-bold">3</span>
            </div>
            <h4 className="font-semibold text-gray-900 mb-2">Action Review</h4>
            <p className="text-sm text-gray-600">Regularly review whether your actions reflect this core concept</p>
          </div>
        </div>
      </div>

      {/* Final Blessing */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-8 text-center">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">Blessing from the Answer Book</h3>
        <p className="text-gray-700 leading-relaxed mb-4">
          Through this deep conversation analysis, you have found the answers within your heart. This proverb will become
          a guiding light on your journey, helping you find direction in confusion and strength in difficulties.
        </p>
        <p className="text-lg font-medium text-purple-600">
          May you carry this wisdom and bravely walk toward your own future.
        </p>
      </div>

      {/* Core Principle Reminder */}
      <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
        <p className="text-center text-gray-700 italic">
          "Language shapes thought, thought guides action."
        </p>
        <p className="text-center text-sm text-gray-500 mt-1">
          — Core Principle of Action Anchor Forging
        </p>
      </div>
    </div>
  );
}
