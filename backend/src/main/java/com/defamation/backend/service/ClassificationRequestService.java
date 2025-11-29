package com.defamation.backend.service;

import com.defamation.backend.repository.ClassificationRequestRepository;
import com.defamation.backend.web.dto.ClassificationRequestDto;
import com.defamation.backend.web.dto.PageResponse;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class ClassificationRequestService {

    private final ClassificationRequestRepository repo;
    private final ObjectMapper om = new ObjectMapper();

    /**
     * 모델 분류 요청 히스토리 검색/페이지네이션
     */
    public PageResponse<ClassificationRequestDto> searchRequests(String q, int page, int size) {
        Pageable pageable = PageRequest.of(page, size);
        Page<ClassificationRequestDto> result = repo.search(q, pageable)
                .map(r -> ClassificationRequestDto.from(r, om));

        return PageResponse.<ClassificationRequestDto>builder()
                .items(result.getContent())
                .page(page)
                .size(size)
                .totalElements(result.getTotalElements())
                .totalPages(result.getTotalPages())
                .build();
    }
}
