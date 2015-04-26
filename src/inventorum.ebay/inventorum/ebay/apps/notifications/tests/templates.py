# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

import datetime
from django.conf import settings
from inventorum.ebay.lib.ebay.notifications import EbayNotification


log = logging.getLogger(__name__)


def compile_notification_template(template, timestamp=None, signature=None, **kwargs):
    if timestamp is None:
        timestamp = datetime.datetime.utcnow()

    timestamp = timestamp.strftime(EbayNotification.TIMESTAMP_FORMAT)

    if signature is None:
        signature = EbayNotification.compute_signature(timestamp, settings.EBAY_DEVID,
                                                       settings.EBAY_APPID, settings.EBAY_CERTID)

    return template(timestamp, signature, **kwargs)


FIXED_PRICE_TRANSACTION_NOTIFICATION = lambda timestamp, signature: """<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
 <soapenv:Header>
  <ebl:RequesterCredentials soapenv:mustUnderstand="0" xmlns:ns="urn:ebay:apis:eBLBaseComponents" xmlns:ebl="urn:ebay:apis:eBLBaseComponents">
   <ebl:NotificationSignature xmlns:ebl="urn:ebay:apis:eBLBaseComponents">{signature}</ebl:NotificationSignature>
  </ebl:RequesterCredentials>
 </soapenv:Header>
 <soapenv:Body>
  <GetItemTransactionsResponse xmlns="urn:ebay:apis:eBLBaseComponents">
   <Timestamp>{timestamp}</Timestamp>
   <Ack>Success</Ack>
   <CorrelationID>586806200</CorrelationID>
   <Version>853</Version>
   <Build>E853_CORE_API_16609591_R1</Build>
   <NotificationEventName>FixedPriceTransaction</NotificationEventName>
   <RecipientUserID>testuser_michalhernas</RecipientUserID>
   <EIASToken>nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6wFk4GhCpiGpAqdj6x9nY+seQ==</EIASToken>
   <PaginationResult>
    <TotalNumberOfPages>1</TotalNumberOfPages>
    <TotalNumberOfEntries>1</TotalNumberOfEntries>
   </PaginationResult>
   <HasMoreTransactions>false</HasMoreTransactions>
   <TransactionsPerPage>100</TransactionsPerPage>
   <PageNumber>1</PageNumber>
   <ReturnedTransactionCountActual>1</ReturnedTransactionCountActual>
   <Item>
    <AutoPay>false</AutoPay>
    <BuyItNowPrice currencyID="EUR">0.0</BuyItNowPrice>
    <Currency>EUR</Currency>
    <ItemID>110136115192</ItemID>
    <ListingDetails>
     <StartTime>2014-01-16T15:19:06.000Z</StartTime>
     <EndTime>2014-01-26T15:19:06.000Z</EndTime>
     <ViewItemURL>http://cgi.sandbox.ebay.de/ws/eBayISAPI.dll?ViewItem&amp;Item=110136115192</ViewItemURL>
     <ExpressListing>false</ExpressListing>
     <ViewItemURLForNaturalSearch>http://cgi.sandbox.ebay.de/ws/eBayISAPI.dll?ViewItem&amp;item=110136115192&amp;category=0</ViewItemURLForNaturalSearch>
    </ListingDetails>
    <ListingType>FixedPriceItem</ListingType>
    <PaymentMethods>PayPal</PaymentMethods>
    <PrimaryCategory>
     <CategoryID>19526</CategoryID>
    </PrimaryCategory>
    <PrivateListing>false</PrivateListing>
    <Quantity>88</Quantity>
    <SecondaryCategory>
     <CategoryID>0</CategoryID>
    </SecondaryCategory>
    <Seller>
     <AboutMePage>false</AboutMePage>
     <EIASToken>nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6wFk4GhCpiGpAqdj6x9nY+seQ==</EIASToken>
     <Email>michal@hernas.pl</Email>
     <FeedbackScore>500</FeedbackScore>
     <PositiveFeedbackPercent>0.0</PositiveFeedbackPercent>
     <FeedbackPrivate>false</FeedbackPrivate>
     <FeedbackRatingStar>Purple</FeedbackRatingStar>
     <IDVerified>true</IDVerified>
     <eBayGoodStanding>true</eBayGoodStanding>
     <NewUser>false</NewUser>
     <RegistrationDate>1995-01-01T00:00:00.000Z</RegistrationDate>
     <Site>Germany</Site>
     <Status>Confirmed</Status>
     <UserID>testuser_michalhernas</UserID>
     <UserIDChanged>false</UserIDChanged>
     <UserIDLastChanged>2013-08-29T08:46:47.000Z</UserIDLastChanged>
     <VATStatus>VATTax</VATStatus>
     <SellerInfo>
      <AllowPaymentEdit>true</AllowPaymentEdit>
      <CheckoutEnabled>true</CheckoutEnabled>
      <CIPBankAccountStored>false</CIPBankAccountStored>
      <GoodStanding>true</GoodStanding>
      <LiveAuctionAuthorized>false</LiveAuctionAuthorized>
      <MerchandizingPref>OptIn</MerchandizingPref>
      <QualifiesForB2BVAT>false</QualifiesForB2BVAT>
      <SellerLevel>None</SellerLevel>
      <StoreOwner>false</StoreOwner>
      <ExpressEligible>false</ExpressEligible>
      <ExpressWallet>false</ExpressWallet>
      <SafePaymentExempt>true</SafePaymentExempt>
     </SellerInfo>
    </Seller>
    <SellingStatus>
     <ConvertedCurrentPrice currencyID="EUR">66.0</ConvertedCurrentPrice>
     <CurrentPrice currencyID="EUR">66.0</CurrentPrice>
     <QuantitySold>3</QuantitySold>
     <ListingStatus>Active</ListingStatus>
    </SellingStatus>
    <Site>Germany</Site>
    <StartPrice currencyID="EUR">66.0</StartPrice>
    <Title>Aba DUPLICATED</Title>
    <GetItFast>false</GetItFast>
    <IntegratedMerchantCreditCardEnabled>false</IntegratedMerchantCreditCardEnabled>
   </Item>
   <TransactionArray>
    <Transaction>
     <AmountPaid currencyID="EUR">0.0</AmountPaid>
     <AdjustmentAmount currencyID="EUR">0.0</AdjustmentAmount>
     <ConvertedAdjustmentAmount currencyID="EUR">0.0</ConvertedAdjustmentAmount>
     <Buyer>
      <AboutMePage>false</AboutMePage>
      <EIASToken>nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6wFk4GhCpiGow6dj6x9nY+seQ==</EIASToken>
      <Email>michal@inventorum.com</Email>
      <FeedbackScore>500</FeedbackScore>
      <PositiveFeedbackPercent>0.0</PositiveFeedbackPercent>
      <FeedbackPrivate>false</FeedbackPrivate>
      <FeedbackRatingStar>Purple</FeedbackRatingStar>
      <IDVerified>true</IDVerified>
      <eBayGoodStanding>true</eBayGoodStanding>
      <NewUser>false</NewUser>
      <RegistrationAddress>
       <Name>Test User</Name>
       <Street>address</Street>
       <Street1>address</Street1>
       <CityName>city</CityName>
       <StateOrProvince>Bad Oyenhausen</StateOrProvince>
       <Country>DE</Country>
       <CountryName>Deutschland</CountryName>
       <Phone>Invalid Request</Phone>
       <PostalCode>32547</PostalCode>
      </RegistrationAddress>
      <RegistrationDate>1995-01-01T00:00:00.000Z</RegistrationDate>
      <Site>Germany</Site>
      <Status>Confirmed</Status>
      <UserID>testuser_inventorum1234</UserID>
      <UserIDChanged>false</UserIDChanged>
      <UserIDLastChanged>2013-08-28T15:17:57.000Z</UserIDLastChanged>
      <VATStatus>VATTax</VATStatus>
      <BuyerInfo>
       <ShippingAddress>
        <Name>Test User</Name>
        <Street1>address</Street1>
        <CityName>city</CityName>
        <StateOrProvince>Bad Oyenhausen</StateOrProvince>
        <Country>DE</Country>
        <CountryName>Deutschland</CountryName>
        <Phone>Invalid Request</Phone>
        <PostalCode>32547</PostalCode>
        <AddressID>6977656</AddressID>
        <AddressOwner>eBay</AddressOwner>
       </ShippingAddress>
      </BuyerInfo>
      <UserAnonymized>false</UserAnonymized>
     </Buyer>
     <ShippingDetails>
      <ChangePaymentInstructions>true</ChangePaymentInstructions>
      <InsuranceFee currencyID="EUR">0.0</InsuranceFee>
      <InsuranceOption>NotOffered</InsuranceOption>
      <InsuranceWanted>false</InsuranceWanted>
      <PaymentEdited>false</PaymentEdited>
      <SalesTax>
       <SalesTaxPercent>0.0</SalesTaxPercent>
       <ShippingIncludedInTax>false</ShippingIncludedInTax>
       <SalesTaxAmount currencyID="EUR">0.0</SalesTaxAmount>
      </SalesTax>
      <ShippingServiceOptions>
       <ShippingService>DE_DHLPackchen</ShippingService>
       <ShippingServiceCost currencyID="EUR">0.0</ShippingServiceCost>
       <ShippingServiceAdditionalCost currencyID="EUR">0.0</ShippingServiceAdditionalCost>
       <ShippingServicePriority>1</ShippingServicePriority>
       <ExpeditedService>false</ExpeditedService>
       <ShippingTimeMin>1</ShippingTimeMin>
       <ShippingTimeMax>2</ShippingTimeMax>
      </ShippingServiceOptions>
      <ShippingType>Flat</ShippingType>
      <SellingManagerSalesRecordNumber>112</SellingManagerSalesRecordNumber>
      <ThirdPartyCheckout>false</ThirdPartyCheckout>
      <TaxTable/>
      <GetItFast>false</GetItFast>
     </ShippingDetails>
     <ConvertedAmountPaid currencyID="EUR">132.0</ConvertedAmountPaid>
     <ConvertedTransactionPrice currencyID="EUR">66.0</ConvertedTransactionPrice>
     <CreatedDate>2014-01-16T15:30:44.000Z</CreatedDate>
     <DepositType>None</DepositType>
     <QuantityPurchased>2</QuantityPurchased>
     <Status>
      <eBayPaymentStatus>NoPaymentFailure</eBayPaymentStatus>
      <CheckoutStatus>CheckoutIncomplete</CheckoutStatus>
      <LastTimeModified>2014-01-16T15:30:45.000Z</LastTimeModified>
      <PaymentMethodUsed>None</PaymentMethodUsed>
      <CompleteStatus>Incomplete</CompleteStatus>
      <BuyerSelectedShipping>false</BuyerSelectedShipping>
      <PaymentHoldStatus>None</PaymentHoldStatus>
      <IntegratedMerchantCreditCardEnabled>false</IntegratedMerchantCreditCardEnabled>
     </Status>
     <TransactionID>27209385001</TransactionID>
     <TransactionPrice currencyID="EUR">66.0</TransactionPrice>
     <BestOfferSale>false</BestOfferSale>
     <ShippingServiceSelected>
      <ShippingInsuranceCost currencyID="EUR">0.0</ShippingInsuranceCost>
      <ShippingService>DE_DHLPackchen</ShippingService>
      <ShippingServiceCost currencyID="EUR">0.0</ShippingServiceCost>
     </ShippingServiceSelected>
     <FinalValueFee currencyID="EUR">10.32</FinalValueFee>
     <TransactionPlatform>eBay</TransactionPlatform>
     <TransactionSiteID>Germany</TransactionSiteID>
     <Platform>eBay</Platform>
     <PayPalEmailAddress>ferry@inventorum.com</PayPalEmailAddress>
     <BuyerGuaranteePrice currencyID="EUR">20000.0</BuyerGuaranteePrice>
     <IntangibleItem>false</IntangibleItem>
    </Transaction>
   </TransactionArray>
  </GetItemTransactionsResponse>
 </soapenv:Body>
</soapenv:Envelope>""".format(timestamp=timestamp, signature=signature)
