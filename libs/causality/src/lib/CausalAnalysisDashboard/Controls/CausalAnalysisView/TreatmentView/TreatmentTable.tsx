// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import {
  defaultModelAssessmentContext,
  ICausalPolicyTreeInternal,
  ICausalPolicyTreeLeaf,
  ModelAssessmentContext
} from "@responsible-ai/core-ui";
import { localization } from "@responsible-ai/localization";
import { Stack, Text } from "office-ui-fabric-react";
import React from "react";

import { TreatmentTableStyles } from "./TreatmentTableStyles";

export interface ITreatmentTableProps {
  data?: ICausalPolicyTreeInternal | ICausalPolicyTreeLeaf;
  horizontal?: boolean;
  innerTable?: boolean;
}

export class TreatmentTable extends React.PureComponent<ITreatmentTableProps> {
  public static contextType = ModelAssessmentContext;
  public context: React.ContextType<typeof ModelAssessmentContext> =
    defaultModelAssessmentContext;

  public render(): React.ReactNode {
    const styles = TreatmentTableStyles();
    if (!this.props.data) {
      return <div>{localization.CausalAnalysis.TreatmentPolicy.noData}</div>;
    }
    if (this.props.data.leaf) {
      return (
        <Stack horizontal={false} grow tokens={{ padding: "l1" }}>
          <Stack.Item>
            <Text>
              {localization.formatString(
                localization.CausalAnalysis.TreatmentPolicy.nSample,
                this.props.data.n_samples
              )}
            </Text>
          </Stack.Item>
          <Stack.Item>
            <Text>
              {localization.formatString(
                localization.CausalAnalysis.TreatmentPolicy.Recommended,
                this.props.data.treatment
              )}
            </Text>
          </Stack.Item>
        </Stack>
      );
    }
    if (!this.props.horizontal) {
      return (
        <table
          className={this.props.innerTable ? styles.tableInner : styles.table}
        >
          <tr>
            <td className={styles.td}>
              {localization.formatString(
                localization.CausalAnalysis.TreatmentPolicy.Left,
                this.props.data.feature,
                this.props.data.threshold
              )}
            </td>
            <td className={styles.td}>
              <TreatmentTable
                data={this.props.data.left}
                horizontal={!this.props.horizontal}
                innerTable
              />
            </td>
          </tr>
          <tr>
            <td className={styles.td}>
              {localization.formatString(
                localization.CausalAnalysis.TreatmentPolicy.Right,
                this.props.data.feature,
                this.props.data.threshold
              )}
            </td>
            <td className={styles.td}>
              <TreatmentTable
                data={this.props.data.right}
                horizontal={!this.props.horizontal}
                innerTable
              />
            </td>
          </tr>
        </table>
      );
    }
    return (
      <table
        className={this.props.innerTable ? styles.tableInner : styles.table}
      >
        <tr>
          <td className={styles.td}>
            {localization.formatString(
              localization.CausalAnalysis.TreatmentPolicy.Left,
              this.props.data.feature,
              this.props.data.threshold
            )}
          </td>
          <td className={styles.td}>
            {localization.formatString(
              localization.CausalAnalysis.TreatmentPolicy.Right,
              this.props.data.feature,
              this.props.data.threshold
            )}
          </td>
        </tr>
        <tr>
          <td className={styles.td}>
            <TreatmentTable
              data={this.props.data.left}
              horizontal={!this.props.horizontal}
              innerTable
            />
          </td>
          <td className={styles.td}>
            <TreatmentTable
              data={this.props.data.right}
              horizontal={!this.props.horizontal}
              innerTable
            />
          </td>
        </tr>
      </table>
    );
  }
}
