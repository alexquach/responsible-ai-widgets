// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import {
  defaultModelAssessmentContext,
  ModelAssessmentContext
} from "@responsible-ai/core-ui";
import { localization } from "@responsible-ai/localization";
import {
  DetailsList,
  DetailsListLayoutMode,
  IColumn,
  SelectionMode
} from "office-ui-fabric-react";
import React from "react";

import { TreatmentStyles } from "./TreatmentStyles";

export interface ITreatmentListProps {
  data?: Array<{ [key: string]: any }>;
  topN: number;
}

export class TreatmentList extends React.Component<ITreatmentListProps> {
  public static contextType = ModelAssessmentContext;
  public context: React.ContextType<typeof ModelAssessmentContext> =
    defaultModelAssessmentContext;

  public render(): React.ReactNode {
    if (!this.props.data) {
      return <>No Data</>;
    }
    const styles = TreatmentStyles();
    const defaultColumns: IColumn[] = [
      {
        fieldName: "Treatment",
        key: "Treatment",
        maxWidth: 400,
        minWidth: 175,
        name: localization.Counterfactuals.RecommendedTreatment
      },
      {
        fieldName: "Effect of treatment",
        isSorted: true,
        isSortedDescending: false,
        key: "Effect of treatment",
        maxWidth: 300,
        minWidth: 150,
        name: localization.Counterfactuals.EffectOfTreatment
      },
      {
        fieldName: "Effect of treatment lower bound",
        key: "Effect of treatment lower bound",
        maxWidth: 300,
        minWidth: 150,
        name: localization.Counterfactuals.EffectLowerBound
      },
      {
        fieldName: "Effect of treatment upper bound",
        key: "Effect of treatment upper bound",
        maxWidth: 300,
        minWidth: 150,
        name: localization.Counterfactuals.EffectUpperBound
      }
    ];
    const defaultKeys = new Set(defaultColumns.map((t) => t.fieldName));
    const allKeys = Object.keys(this.props.data[0]);
    const leftKeys = allKeys.filter((c) => !defaultKeys.has(c));
    const leftColumns = leftKeys.map((k) => {
      return {
        fieldName: k,
        key: k,
        maxWidth: 100,
        minWidth: 75,
        name: k
      };
    });
    const columns = [...defaultColumns, ...leftColumns];
    const maxCount = Math.min(this.props.data.length, this.props.topN);
    const items = this.props.data
      .sort((a, b) => b["Effect of treatment"] - a["Effect of treatment"])
      .slice(0, maxCount);
    return (
      <div className={styles.listContainer}>
        <DetailsList
          items={items}
          columns={columns}
          selectionMode={SelectionMode.none}
          setKey="set"
          layoutMode={DetailsListLayoutMode.justified}
        />
      </div>
    );
  }
}
