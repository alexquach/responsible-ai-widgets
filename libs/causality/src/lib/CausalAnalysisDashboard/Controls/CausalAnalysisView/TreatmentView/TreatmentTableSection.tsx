// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import {
  defaultModelAssessmentContext,
  ICausalPolicy,
  ModelAssessmentContext
} from "@responsible-ai/core-ui";
import { localization } from "@responsible-ai/localization";
import { Stack, Text } from "office-ui-fabric-react";
import React from "react";

import { TreatmentCell } from "./TreatmentCell";
import { TreatmentTable } from "./TreatmentTable";
import { TreatmentTableStyles } from "./TreatmentTableStyles";

export interface ITreatmentTableSectionProps {
  data?: ICausalPolicy;
}

export class TreatmentTableSection extends React.Component<ITreatmentTableSectionProps> {
  public static contextType = ModelAssessmentContext;
  public context: React.ContextType<typeof ModelAssessmentContext> =
    defaultModelAssessmentContext;

  public render(): React.ReactNode {
    const styles = TreatmentTableStyles();
    return (
      <Stack horizontal={false} grow tokens={{ padding: "l1" }}>
        <Stack.Item>
          <Text variant={"medium"} className={styles.header}>
            {localization.formatString(
              localization.CausalAnalysis.TreatmentPolicy.Size,
              this.props.data?.local_policies?.length
            )}
          </Text>
        </Stack.Item>
        <Stack.Item>
          <Stack horizontal grow tokens={{ padding: "l1" }}>
            <Stack.Item>
              {this.props.data?.policy_tree?.leaf ? (
                <TreatmentCell data={this.props.data?.policy_tree} />
              ) : (
                <TreatmentTable data={this.props.data?.policy_tree} />
              )}
            </Stack.Item>
            <Stack.Item>
              <Text variant={"medium"} className={styles.label}>
                {localization.CausalAnalysis.TreatmentPolicy.TableDescription}
              </Text>
              <Text variant={"medium"} className={styles.label}>
                {localization.CausalAnalysis.TreatmentPolicy.Table}
              </Text>
            </Stack.Item>
          </Stack>
        </Stack.Item>
      </Stack>
    );
  }
}
