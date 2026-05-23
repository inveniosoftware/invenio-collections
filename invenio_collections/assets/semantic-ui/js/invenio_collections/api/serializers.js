/*
 * SPDX-FileCopyrightText: 2026 CERN.
 * SPDX-License-Identifier: MIT
 */

export const communityErrorSerializer = (error) => ({
  message: error?.response?.data?.message,
  errors: error?.response?.data?.errors,
  status: error?.response?.data?.status,
});
