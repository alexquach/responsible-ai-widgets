// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import {
  IErrorAnalysisMatrix,
  IExplanationDashboardData,
  ISerializedExplanationData
} from "@responsible-ai/core-ui";
import {
  ErrorAnalysisDashboard,
  IErrorAnalysisDashboardProps,
  HelpMessageDict
} from "@responsible-ai/error-analysis";
import { Language } from "@responsible-ai/localization";
import { ITheme } from "office-ui-fabric-react";
import React from "react";

import {
  createJsonImportancesGenerator,
  createPredictionsRequestGenerator,
  generateJsonMatrix,
  generateJsonTreeAdultCensusIncome,
  generateJsonTreeBreastCancer,
  generateJsonTreeBoston,
  getJsonMatrix,
  getJsonTreeAdultCensusIncome,
  getJsonTreeBreastCancer,
  getJsonTreeBoston,
  DatasetName
} from "./utils";

interface IAppProps {
  dataset: IExplanationDashboardData | ISerializedExplanationData;
  theme: ITheme;
  language: Language;
  version: 1 | 2 | 3;
  classDimension?: 1 | 2 | 3;
}

export class App extends React.Component<IAppProps> {
  private messages: HelpMessageDict = {
    LocalExpAndTestReq: [{ displayText: "LocalExpAndTestReq", format: "text" }],
    LocalOrGlobalAndTestReq: [
      { displayText: "LocalOrGlobalAndTestReq", format: "text" }
    ],
    PredictorReq: [{ displayText: "PredictorReq", format: "text" }],
    TestReq: [{ displayText: "TestReq", format: "text" }]
  };

  public render(): React.ReactNode {
    let requestPredictionsMethod = undefined;
    let requestMatrixMethod = undefined;
    let requestDebugMLMethod = undefined;
    let requestImportancesMethod = undefined;

    requestPredictionsMethod = async (data: any[]): Promise<any[]> => {
      return callFlaskService(data, "/predict");
    };
    requestMatrixMethod = async (
      data: any[]
    ): Promise<IErrorAnalysisMatrix> => {
      return callFlaskService(data, "/matrix");
    };
    requestDebugMLMethod = async (data: any[]): Promise<any[]> => {
      return callFlaskService(data, "/tree");
    };
    requestImportancesMethod = async (data: any[]): Promise<any[]> => {
      return callFlaskService(data, "/importances");
    };
    let dashboardProp: IErrorAnalysisDashboardProps;
    if (this.props.classDimension === 1) {
      const dataset = this.props.dataset as IExplanationDashboardData;
      const featureNames = dataset.dataSummary.featureNames
        ? dataset.dataSummary.featureNames
        : [];
      if (this.props.version === 1) {
        dashboardProp = {
          ...dataset,
          explanationMethod: "mimic",
          features: featureNames,
          locale: this.props.language,
          localUrl: "https://www.bing.com/",
          requestDebugML: generateJsonTreeBoston,
          requestImportances: createJsonImportancesGenerator(
            "dataSummary" in this.props.dataset &&
              this.props.dataset.dataSummary.featureNames
              ? this.props.dataset.dataSummary.featureNames
              : [],
            DatasetName.Boston
          ),
          requestMatrix: generateJsonMatrix,
          requestPredictions: !this.props.classDimension
            ? undefined
            : createPredictionsRequestGenerator(this.props.classDimension),
          stringParams: { contextualHelp: this.messages },
          theme: this.props.theme
        };
      } else if (this.props.version === 3) {
        dashboardProp = {
          ...dataset,
          explanationMethod: "mimic",
          features: featureNames,
          locale: this.props.language,
          localUrl: "https://www.bing.com/",
          requestDebugML: requestDebugMLMethod,
          requestImportances: requestImportancesMethod,
          requestMatrix: requestMatrixMethod,
          requestPredictions: requestPredictionsMethod,
          stringParams: { contextualHelp: this.messages },
          theme: this.props.theme
        };
      } else {
        dashboardProp = {
          ...dataset,
          explanationMethod: "mimic",
          features: featureNames,
          locale: this.props.language,
          localUrl: "https://www.bing.com/",
          staticDebugML: getJsonTreeBoston(featureNames),
          staticMatrix: getJsonMatrix(),
          stringParams: { contextualHelp: this.messages },
          theme: this.props.theme
        };
      }
      return <ErrorAnalysisDashboard {...dashboardProp} />;
    }
    if ("categoricalMap" in this.props.dataset) {
      if (this.props.version === 1) {
        return (
          <ErrorAnalysisDashboard
            modelInformation={{ modelClass: "blackbox" }}
            dataSummary={{
              categoricalMap: this.props.dataset.categoricalMap,
              classNames: this.props.dataset.classNames,
              featureNames: this.props.dataset.featureNames
            }}
            testData={this.props.dataset.trainingData}
            predictedY={this.props.dataset.predictedY as any}
            probabilityY={this.props.dataset.probabilityY}
            trueY={this.props.dataset.trueY as any}
            precomputedExplanations={{
              localFeatureImportance: this.props.dataset.localExplanations
            }}
            requestPredictions={
              !this.props.classDimension
                ? undefined
                : createPredictionsRequestGenerator(this.props.classDimension)
            }
            requestDebugML={generateJsonTreeAdultCensusIncome}
            requestMatrix={generateJsonMatrix}
            requestImportances={createJsonImportancesGenerator(
              this.props.dataset.featureNames,
              DatasetName.AdultCensusIncome
            )}
            localUrl={""}
            locale={undefined}
            features={this.props.dataset.featureNames}
          />
        );
      } else if (this.props.version === 3) {
        return (
          <ErrorAnalysisDashboard
            modelInformation={{ modelClass: "blackbox" }}
            dataSummary={{
              categoricalMap: this.props.dataset.categoricalMap,
              classNames: this.props.dataset.classNames,
              featureNames: this.props.dataset.featureNames
            }}
            testData={this.props.dataset.trainingData}
            predictedY={this.props.dataset.predictedY as any}
            probabilityY={this.props.dataset.probabilityY}
            trueY={this.props.dataset.trueY as any}
            precomputedExplanations={{
              localFeatureImportance: this.props.dataset.localExplanations
            }}
            requestDebugML={requestDebugMLMethod}
            requestImportances={requestImportancesMethod}
            requestMatrix={requestMatrixMethod}
            requestPredictions={requestPredictionsMethod}
            localUrl={""}
            locale={undefined}
            features={this.props.dataset.featureNames}
          />
        );
      }
      return (
        <ErrorAnalysisDashboard
          modelInformation={{ modelClass: "blackbox" }}
          dataSummary={{
            categoricalMap: this.props.dataset.categoricalMap,
            classNames: this.props.dataset.classNames,
            featureNames: this.props.dataset.featureNames
          }}
          testData={this.props.dataset.trainingData}
          predictedY={this.props.dataset.predictedY as any}
          probabilityY={this.props.dataset.probabilityY}
          trueY={this.props.dataset.trueY as any}
          precomputedExplanations={{
            localFeatureImportance: this.props.dataset.localExplanations
          }}
          staticDebugML={getJsonTreeAdultCensusIncome(
            this.props.dataset.featureNames
          )}
          staticMatrix={getJsonMatrix()}
          localUrl={""}
          locale={undefined}
          features={this.props.dataset.featureNames}
        />
      );
    }
    if (this.props.version === 1) {
      const dataset = this.props.dataset as IExplanationDashboardData;
      dashboardProp = {
        ...dataset,
        explanationMethod: "mimic",
        features: dataset.dataSummary.featureNames
          ? dataset.dataSummary.featureNames
          : [],
        locale: this.props.language,
        localUrl: "https://www.bing.com/",
        requestDebugML: generateJsonTreeBreastCancer,
        requestImportances: createJsonImportancesGenerator(
          "dataSummary" in this.props.dataset &&
            this.props.dataset.dataSummary.featureNames
            ? this.props.dataset.dataSummary.featureNames
            : [],
          DatasetName.BreastCancer
        ),
        requestMatrix: generateJsonMatrix,
        requestPredictions: !this.props.classDimension
          ? undefined
          : createPredictionsRequestGenerator(this.props.classDimension),
        stringParams: { contextualHelp: this.messages },
        theme: this.props.theme
      };
    } else if (this.props.version === 3) {
      const dataset = this.props.dataset as IExplanationDashboardData;
      dashboardProp = {
        ...dataset,
        explanationMethod: "mimic",
        features: dataset.dataSummary.featureNames
          ? dataset.dataSummary.featureNames
          : [],
        locale: this.props.language,
        localUrl: "https://www.bing.com/",
        requestDebugML: requestDebugMLMethod,
        requestImportances: requestImportancesMethod,
        requestMatrix: requestMatrixMethod,
        requestPredictions: requestPredictionsMethod,
        stringParams: { contextualHelp: this.messages },
        theme: this.props.theme
      };
    } else {
      const dataset = this.props.dataset as IExplanationDashboardData;
      const featureNames = dataset.dataSummary.featureNames
        ? dataset.dataSummary.featureNames
        : [];
      dashboardProp = {
        ...(this.props.dataset as IExplanationDashboardData),
        explanationMethod: "mimic",
        features: featureNames,
        locale: this.props.language,
        localUrl: "https://www.bing.com/",
        staticDebugML: getJsonTreeBreastCancer(featureNames),
        staticMatrix: getJsonMatrix(),
        stringParams: { contextualHelp: this.messages },
        theme: this.props.theme
      };
    }
    return <ErrorAnalysisDashboard {...dashboardProp} />;
  }
}

export async function callFlaskService<TRequest, TResponse>(
  data: TRequest,
  urlPath: string
): Promise<TResponse> {
  const url = "http://localhost:5000" + urlPath;
  return fetch(url, {
    body: JSON.stringify(data),
    headers: {
      "Content-Type": "application/json"
    },
    method: "post"
  })
    .then((resp) => {
      if (resp.status >= 200 && resp.status < 300) {
        return resp.json();
      }
      return Promise.reject(new Error(resp.statusText));
    })
    .then((json) => {
      if (json.error !== undefined) {
        throw new Error(json.error);
      }
      return Promise.resolve(json.data);
    });
}
