-- Base transactions table that pulls from source tables
-- References actual source tables from shopify_airflow database


with customer_source_table as (
    select 
        id,
        legacyResourceId,
        displayName,
        defaultEmailAddress,
        defaultPhoneNumber,
        emailVerified,
        locale,
        state,
        companyContactProfiles,
        addresses,
        addressesV2,
        defaultAddress,
        image,
        amountSpent,
        numberOfOrders,
        lifetimeDuration,
        orders,
        lastOrder,
        statistics,
        events,
        tags,
        taxExempt,
        taxExemptions,
        storeCreditAccounts,
        subscriptionContracts,
        productSubscriberStatus,
        canDelete,
        dataSaleOptOut,
        mergeable,
        note,
        multipassIdentifier
    from {{ source('shopify_customer', 'customer') }}
),

select * from customer_source_table 