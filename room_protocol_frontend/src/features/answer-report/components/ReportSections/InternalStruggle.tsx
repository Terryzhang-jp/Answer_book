import React from 'react';
import { Users, MessageSquare, Trophy } from 'lucide-react';
import { InternalStruggle } from '../../types/report';

interface InternalStruggleSectionProps {
  data: InternalStruggle;
}

export default function InternalStruggleSection({ data }: InternalStruggleSectionProps) {
  return (
    <div className="space-y-8">
      {/* Title */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Part 2: Internal Struggle Analysis</h2>
        <p className="text-gray-600">Presenting invisible inner thought battles in an objective, visualized manner</p>
      </div>

      {/* Contending Parties */}
      <div className="bg-purple-50 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <Users className="w-6 h-6 text-purple-600 mr-3" />
          <h3 className="text-xl font-semibold text-gray-900">Contending Parties</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data.contending_parties.map((party, index) => (
            <div key={index} className="bg-white rounded-lg p-4 border-2 border-purple-200">
              <div className="text-center">
                <div className={`w-12 h-12 rounded-full mx-auto mb-3 flex items-center justify-center ${
                  index === 0 ? 'bg-blue-100 text-blue-600' : 'bg-orange-100 text-orange-600'
                }`}>
                  <span className="font-bold text-lg">{index === 0 ? 'A' : 'B'}</span>
                </div>
                <h4 className="font-semibold text-gray-900">{party}</h4>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Evidence List */}
      <div className="bg-indigo-50 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <MessageSquare className="w-6 h-6 text-indigo-600 mr-3" />
          <h3 className="text-xl font-semibold text-gray-900">Evidence List</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Party 1 Evidence */}
          <div className="bg-white rounded-lg p-4 border-l-4 border-blue-500">
            <h4 className="font-semibold text-blue-600 mb-3">{data.contending_parties[0]}</h4>
            <div className="space-y-3">
              {data.evidence_list.party1?.map((evidence, index) => (
                <div key={index} className="border-b border-gray-100 pb-2 last:border-b-0">
                  <div className="flex items-center mb-1">
                    <span className="text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded">
                      {evidence.type}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700 mb-1">{evidence.content}</p>
                  <blockquote className="text-xs text-gray-500 italic border-l-2 border-gray-200 pl-2">
                    "{evidence.quote}"
                  </blockquote>
                </div>
              ))}
            </div>
          </div>

          {/* Party 2 Evidence */}
          <div className="bg-white rounded-lg p-4 border-l-4 border-orange-500">
            <h4 className="font-semibold text-orange-600 mb-3">{data.contending_parties[1]}</h4>
            <div className="space-y-3">
              {data.evidence_list.party2?.map((evidence, index) => (
                <div key={index} className="border-b border-gray-100 pb-2 last:border-b-0">
                  <div className="flex items-center mb-1">
                    <span className="text-xs bg-orange-100 text-orange-600 px-2 py-1 rounded">
                      {evidence.type}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700 mb-1">{evidence.content}</p>
                  <blockquote className="text-xs text-gray-500 italic border-l-2 border-gray-200 pl-2">
                    "{evidence.quote}"
                  </blockquote>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Struggle Outcome */}
      <div className="bg-yellow-50 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <Trophy className="w-6 h-6 text-yellow-600 mr-3" />
          <h3 className="text-xl font-semibold text-gray-900">Struggle Outcome</h3>
        </div>
        <div className="bg-white rounded-lg p-6 border-l-4 border-yellow-500">
          <p className="text-gray-800 leading-relaxed">{data.outcome}</p>
        </div>
      </div>

      {/* Core Principle Reminder */}
      <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
        <p className="text-center text-gray-700 italic">
          "Your actions and words are votes for your inner values."
        </p>
        <p className="text-center text-sm text-gray-500 mt-1">
          — Core Principle of Internal Struggle Analysis
        </p>
      </div>
    </div>
  );
}
