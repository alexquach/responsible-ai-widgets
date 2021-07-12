// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import { IBounds } from "@responsible-ai/core-ui";
import { localization } from "@responsible-ai/localization";
import _ from "lodash";
import {
  Stack,
  Dropdown,
  Toggle,
  IDropdownOption,
  ActionButton,
  Modal,
  IconButton,
  PrimaryButton,
  IIconProps
} from "office-ui-fabric-react";
import React from "react";

import {
  IPerformancePickerPropsV2,
  IFairnessPickerPropsV2,
  IErrorPickerPropsV2,
  IFeatureBinPickerPropsV2
} from "../FairnessWizard";

import { IFairnessContext } from "./../util/IFairnessContext";
import { DropdownBarStyles } from "./DropdownBar.styles";

export interface IDropdownBarProps {
  dashboardContext: IFairnessContext;
  performancePickerProps: IPerformancePickerPropsV2;
  fairnessPickerProps: IFairnessPickerPropsV2;
  errorPickerProps: IErrorPickerPropsV2;
  featureBinPickerProps: IFeatureBinPickerPropsV2;
  parentPerformanceChanged: {
    (_ev: React.FormEvent<HTMLDivElement>, option?: IDropdownOption): void;
  };
  parentFairnessChanged: {
    (_ev: React.FormEvent<HTMLDivElement>, option?: IDropdownOption): void;
  };
  parentFeatureChanged: {
    (_ev: React.FormEvent<HTMLDivElement>, option?: IDropdownOption): void;
  };
  parentErrorChanged: {
    (event: React.MouseEvent<HTMLElement>, checked?: boolean): void;
  };
  fairnessBounds?: Array<IBounds | undefined>;
  performanceBounds?: Array<IBounds | undefined>;
  outcomeBounds?: Array<IBounds | undefined>;
  falsePositiveBounds?: Array<IBounds | undefined>;
  falseNegativeBounds?: Array<IBounds | undefined>;
}

export interface IState {
  showModalHelp?: boolean;
}

export class DropdownBar extends React.PureComponent<
  IDropdownBarProps,
  IState
> {
  public render(): React.ReactNode {
    const styles = DropdownBarStyles();
    const featureOptions: IDropdownOption[] = this.props.dashboardContext.modelMetadata.featureNames.map(
      (x) => {
        return { key: x, text: x };
      }
    );
    const performanceDropDown: IDropdownOption[] = this.props.performancePickerProps.performanceOptions.map(
      (x) => {
        return { key: x.key, text: x.title };
      }
    );
    const fairnessDropdown: IDropdownOption[] = this.props.fairnessPickerProps.fairnessOptions.map(
      (x) => {
        return { key: x.key, text: x.title };
      }
    );

    const cancelIcon: IIconProps = { iconName: "Cancel" };

    const howTo = (
      <Stack className={styles.toolTipWrapper}>
        <Stack>{localization.Fairness.DropdownHeaders.errorMetric}</Stack>
        <Stack>
          <ActionButton
            className={styles.actionButton}
            onClick={this.handleOpenModalHelp}
          >
            <div className={styles.infoButton}>i</div>
            {localization.Fairness.ErrorBounds.howToRead}
          </ActionButton>
          <Modal
            titleAriaId="help modal"
            isOpen={this.state?.showModalHelp}
            onDismiss={this.handleCloseModalHelp}
            isModeless
            containerClassName={styles.modalContentHelp}
          >
            <IconButton
              iconProps={cancelIcon}
              ariaLabel="Close popup modal"
              onClick={this.handleCloseModalHelp}
            />
            <p className={styles.modalContentHelpText}>
              {localization.Fairness.ErrorBounds.introModalText}
              <br />
              <br />
            </p>
            <div style={{ display: "flex", paddingBottom: "20px" }}>
              <PrimaryButton
                className={styles.doneButton}
                onClick={this.handleCloseModalHelp}
              >
                {localization.Fairness.done}
              </PrimaryButton>
            </div>
          </Modal>
        </Stack>
      </Stack>
    );

    return (
      <Stack horizontal tokens={{ childrenGap: "l1", padding: "0 100px" }}>
        <Dropdown
          id="sensitiveFeatureDropdown"
          label={localization.Fairness.DropdownHeaders.sensitiveFeature}
          defaultSelectedKey={
            this.props.dashboardContext.modelMetadata.featureNames[
              this.props.featureBinPickerProps.selectedBinIndex
            ]
          }
          options={featureOptions}
          disabled={false}
          onChange={this.props.parentFeatureChanged}
        />
        <Dropdown
          id="performanceMetricDropdown"
          label={localization.Fairness.DropdownHeaders.performanceMetric}
          defaultSelectedKey={
            this.props.performancePickerProps.selectedPerformanceKey
          }
          options={performanceDropDown}
          disabled={false}
          onChange={this.props.parentPerformanceChanged}
        />
        <Dropdown
          style={{ minWidth: "240px" }}
          id="fairnessMetricDropdown"
          label={localization.Fairness.DropdownHeaders.fairnessMetric}
          defaultSelectedKey={
            this.props.fairnessPickerProps.selectedFairnessKey
          }
          options={fairnessDropdown}
          disabled={false}
          onChange={this.props.parentFairnessChanged}
        />
        <Toggle
          id="errorMetricDropdown"
          label={howTo}
          defaultChecked={
            this.props.errorPickerProps.selectedErrorKey === "enabled"
          }
          disabled={
            (typeof this.props.fairnessBounds === "undefined" ||
              _.isEmpty(this.props.fairnessBounds.filter(Boolean))) &&
            (typeof this.props.performanceBounds === "undefined" ||
              _.isEmpty(this.props.performanceBounds.filter(Boolean))) &&
            (typeof this.props.outcomeBounds === "undefined" ||
              _.isEmpty(this.props.outcomeBounds.filter(Boolean))) &&
            (typeof this.props.falseNegativeBounds === "undefined" ||
              _.isEmpty(this.props.falseNegativeBounds.filter(Boolean))) &&
            (typeof this.props.falsePositiveBounds === "undefined" ||
              _.isEmpty(this.props.falsePositiveBounds.filter(Boolean)))
          }
          onChange={this.props.parentErrorChanged}
        />
      </Stack>
    );
  }
  private readonly handleOpenModalHelp = (): void => {
    this.setState({ showModalHelp: true });
  };

  private readonly handleCloseModalHelp = (): void => {
    this.setState({ showModalHelp: false });
  };
}
